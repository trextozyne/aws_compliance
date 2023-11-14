import sys

import boto3
from botocore.exceptions import ClientError


class S3:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.cloudtrail_client = boto3.client('cloudtrail')

    def s3_compliance(self, event):
        # Check if the event is related to S3
        if 'Records' in event and event['Records'][0]['eventSource'] == 'aws:s3':
            bucket_name = event['detail']['requestParameters']['bucketName']
            self.check_and_update_bucket_compliance(bucket_name)
        else:
            return event

    def update_bucket_compliance(self, bucket_name):
        self.check_bucket_access_policy(bucket_name)
        self.make_bucket_private(bucket_name)
        self.enable_bucket_encryption(bucket_name)
        self.enable_bucket_logging(bucket_name)
        self.enable_bucket_versioning(bucket_name)
        self.set_bucket_lifecycle_configuration(bucket_name)

    def check_and_update_bucket_compliance(self, bucket_name):
        try:
            # Check for the compliance tag for the specified bucket
            response = self.s3_client.get_bucket_tagging(Bucket=bucket_name)

            if not any(tag['Key'] == 'compliance' or tag['Value'] == 'no' for tag in response['TagSet']):
                self.update_bucket_compliance(bucket_name)
        except Exception as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                print(e)# self.update_bucket_compliance(bucket_name)

    def make_bucket_private(self, bucket_name):
        count = 1

        try:
            # Get the public access block configuration
            response = self.s3_client.get_public_access_block(Bucket=bucket_name)
            public_access_block = response['PublicAccessBlockConfiguration']

            # Check if public access is blocked
            if public_access_block['BlockPublicAcls'] and public_access_block['BlockPublicPolicy'] and \
                    public_access_block['IgnorePublicAcls'] and public_access_block['RestrictPublicBuckets']:
                print(f'Bucket {bucket_name} is compliant')
            else:
                self.s3_client.put_public_access_block(Bucket=bucket_name, PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                })
                print(f'Updated public access block configuration for bucket {bucket_name}')
        except self.s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
            print(f'Bucket {bucket_name} does not have a public access block configuration')

        except Exception as e:
            print(f'Error: {e}')

        try:
            # Check ACLs to see if grantee is AllUsers or AuthenticatedUsers groups
            response = self.s3_client.get_bucket_acl(Bucket=bucket_name)
            grants = response['Grants']
            grants_len = len(grants)
            for grant in grants:
                if 'URI' in grant['Grantee'] and grant['Grantee']['URI'] == 'https://acs.amazonaws.com/groups/global' \
                                                                            '/AllUsers':
                    self.s3_client.put_bucket_acl(Bucket=bucket_name, ACL='private')
                    count += 1

            if count == grants_len:
                print(f'Bucket {bucket_name} is compliant')
        except Exception as e:
            print(f'An error occurred while checking and updating ACLs for bucket {bucket_name}: {e}')


    def check_bucket_access_policy(self, bucket_name):
        try:
            response = self.cloudtrail_client.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceName',
                        'AttributeValue': bucket_name
                    }
                ]
            )
            for event in response['Events']:
                if event['EventName'] == 'PutBucketAcl' or event['EventName'] == 'PutBucketPolicy':
                    # Check if the bucket policy or ACL allows public access
                    response = self.s3_client.get_bucket_policy_status(Bucket=bucket_name)
                    if response['PolicyStatus']['IsPublic']:
                        # Deny public access to the bucket
                        self.s3_client.put_bucket_policy(
                            Bucket=bucket_name,
                            Policy='{"Version":"2012-10-17","Statement":[{"Sid":"DenyPublicAccess","Effect":"Deny",'
                                   '"Principal":"*","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::' +
                                   bucket_name + '/*"],"Condition":{"StringNotEquals":{"aws:Referer":['
                                                 '"https://www.example.com/*"]}}}]}" '
                        )
        except self.s3_client.exceptions.NoSuchBucket:
            print(f'Bucket {bucket_name} does not have a bucket policy')
        except Exception as e:
            print(f"An error occurred: {e}")

    def enable_bucket_encryption(self, bucket_name):
        response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
        if 'ServerSideEncryptionConfiguration' not in response:
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )

    def enable_bucket_logging(self, bucket_name):
        response = self.s3_client.get_bucket_logging(Bucket=bucket_name)
        if 'LoggingEnabled' not in response:
            self.s3_client.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': bucket_name,
                        'TargetPrefix': 'logs/'
                    }
                }
            )

    def enable_bucket_versioning(self, bucket_name):
        response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
        if response.get('Status') != 'Enabled':
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )

    def set_bucket_lifecycle_configuration(self, bucket_name):
        try:
            lifecycle_config = self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                lifecycle_config = None
            else:
                raise e

        if not lifecycle_config or not lifecycle_config.get('Rules'):
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    # must be one of: Expiration, ID, Prefix, Filter, Status, Transitions,
                    # NoncurrentVersionTransitions
                    'Rules': [
                        {
                            'Status': 'Enabled',
                            'Filter': {
                                'Prefix': 'compliance_'
                            },
                            'NoncurrentVersionTransitions': [
                                {
                                    'NoncurrentDays': 30,
                                    'StorageClass': 'GLACIER'
                                }
                            ],
                            'NoncurrentVersionExpiration': {
                                'NoncurrentDays': 90
                            },
                            'AbortIncompleteMultipartUpload': {
                                'DaysAfterInitiation': 7
                            }
                        }
                    ]
                }
            )
