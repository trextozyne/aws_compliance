import re
import logging
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
        if 'eventName' in event['Records'][0] and event['Records'][0]['eventName'] == 'CreateRole':
            # Extract the role name from the event
            role_name = event['requestParameters']['roleName']

            # Get the policy associated with the role
            try:
                policy = self.iam_client.get_role_policy(RoleName=role_name, PolicyName='default')['PolicyDocument']
            except ClientError as e:
                logging.error(f"Error getting policy for role {role_name}: {e}")
                return

            # Check if the policy grants least privilege
            for statement in policy['Statement']:
                if 'Effect' in statement and statement['Effect'] == 'Allow':
                    if 'Action' in statement and isinstance(statement['Action'], list):
                        actions = statement['Action']
                        resource = statement.get('Resource', '')
                        resource_type = re.search(r':([a-z]+)-', resource).group(1) if resource else ''
                        if resource_type in self.resource_actions:
                            necessary_actions = self.resource_actions[resource_type]
                            unnecessary_actions = set(actions) - set(necessary_actions)
                            if unnecessary_actions:
                                # Modify the policy to remove unnecessary actions
                                statement['Action'] = necessary_actions
                                try:
                                    self.iam_client.put_role_policy(RoleName=role_name, PolicyName='default', PolicyDocument=policy)
                                except ClientError as e:
                                    logging.error(f"Error updating policy for role {role_name}: {e}")
