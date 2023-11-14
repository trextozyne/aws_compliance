import re
import logging
import json
import boto3
from botocore.exceptions import ClientError


class IAM:
    def __init__(self):
        # Connect to the IAM client
        self.iam_client = boto3.client('iam')

        # Define the minimum necessary actions for each resource
        self.resource_actions = {
            's3': ['s3:GetObject', 's3:PutObject'],
            'ec2': ['ec2:RunInstances'],
            'dynamodb': ['dynamodb:GetItem', 'dynamodb:PutItem'],
            'rds': ['rds:CreateDBInstance', 'rds:DeleteDBInstance'],
            'cloudwatch': ['cloudwatch:GetMetricStatistics', 'cloudwatch:PutMetricData'],
            'sns': ['sns:Publish'],
            'lambda': ['lambda:InvokeFunction']
        }

    def iam_compliance(self, event):
        # Check if the event is related to IAM role creation
        if event['eventName'] == 'CreateRole':

            # Get the role ARN from the event
            role_arn = event['detail']['requestParameters']['roleName']

            # Get the policy attached to the role
            attached_policy = self.iam_client.get_role_policy(RoleName=role_arn, PolicyName='my-policy')

            # Get the permissions granted in the policy
            policy_permissions = json.loads(attached_policy['PolicyDocument'])['Statement'][0]['Action']

            # Get the resource from the policy
            resource = policy_permissions[0].split(':')[0]

            # Check if the resource is in the dictionary
            if resource in self.resource_actions:
                # If the resource is in the dictionary, use its minimum necessary actions in the policy
                self.iam_client.put_role_policy(
                    RoleName=role_arn,
                    PolicyName='my-policy',
                    PolicyDocument=json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": self.resource_actions[resource],
                                "Resource": "*"
                            }
                        ]
                    })
                )

            # Return a success response
            return {
                'statusCode': 200,
                'body': json.dumps('IAM role access has been remediated.')
            }