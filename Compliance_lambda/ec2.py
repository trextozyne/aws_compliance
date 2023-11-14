import re
import logging
import boto3
from botocore.exceptions import ClientError


class Ec2:
    def __init__(self):
        self.asg_name = "asg-for-test-1"
        self.count = 1

        # Connect to the EC2 client
        self._ec2 = boto3.client('ec2')
        # Connect to the autoscaling client
        self.autoscaling_client = boto3.client('autoscaling')
        # Connect to the cloudtrail client
        self.cloudtrail_client = boto3.client('cloudtrail')

        self.instance_large_family = ['t3.large']
        self.instance_small_family = ['t3.micro']

        self.scale_out_threshold = 80
        self.scale_in_threshold = 30

    def ec2_compliance(self, event):
        # First find & destroy all stale snapshots
        self.destroy_stale_snapshots()

        # Check if the event is related to EC2
        if 'Records' in event and event['Records'][0]['eventSource'] == 'aws.ec2':
            # Get the instance ID from
            # ["responseElements"]["instancesSet"]["items"][0]["instanceId imageId instanceType"]
            if event is not None and event.get("detail") is not None and event["detail"].get("responseElements") is not \
                    None and event["detail"]["responseElements"].get("instancesSet") is not None:
                instance_id = event["detail"]["responseElements"]["instancesSet"]["items"][0]["instanceId"]

                self.perform_instance_autoscaling_group(instance_id)

            elif event['source'] == 'aws.cloudwatch':
                # Get the instance ID from the CloudWatch alarm notification
                instance_id = event['Trigger']['Dimensions'][0]['value']

                self.monitor_cpu_utilization(instance_id)
                self.monitor_memory_utilization(instance_id)
            else:
                return


    def destroy_stale_snapshots(self):
        def delete_snapshot(snapshot_id, reason):
            self._ec2.delete_snapshot(SnapshotId=snapshot_id)
            print(f"Deleted EBS snapshot {snapshot_id} - {reason}")

        def deregister_amis(_amis):
            for ami in _amis:
                ami_id = ami['ImageId']

                # Deregister the AMI
                deregister_response = self._ec2.deregister_image(ImageId=ami_id)

                # Print the response
                print("Deregistering AMI:", deregister_response['ImageId'])

        # Get active instance IDs
        instances_response = self._ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        # This "{...}" is  a set comprehension & "for reservation in instances_response['Reservations']" loop iterates
        # through each reservation in the list of reservations & "for instance in reservation['Instances']"  loop iterates
        # through each instance in the list of instances within the current reservation & then "instance['InstanceId']"
        # extracts the value of the 'InstanceId' key from the current instance.
        active_instance_ids = {instance['InstanceId'] for reservation in instances_response['Reservations'] for instance in reservation['Instances']}

        # Get all EBS snapshots
        response = self._ec2.describe_snapshots(OwnerIds=['self'])

        # Iterate through each snapshot and delete if necessary
        for snapshot in response['Snapshots']:
            snapshot_id = snapshot['SnapshotId']
            amis = snapshot['Images']
            volume_id = snapshot.get('VolumeId')

            #if amis are attached to snapshot, cant be deleted till de-registering
            if amis:
                deregister_amis(amis)
            if not volume_id:
                delete_snapshot(snapshot_id, "not attached to any volume")
            else:
                try:
                    volume_response = self._ec2.describe_volumes(VolumeIds=[volume_id])
                    if not volume_response['Volumes'][0]['Attachments']:
                        delete_snapshot(snapshot_id, "taken from a volume not attached to any running instance")
                except self._ec2.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                        delete_snapshot(snapshot_id, "associated volume not found")

    def get_asg_name(self, asg_name):
        asg_number = int(re.search(r'\d+', asg_name).group())

        # Check if the ASG name already exists
        response = self.autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

        if len(response['AutoScalingGroups']) == 0:
            return asg_name

        # ASG name already exists, increment the number and try again
        new_asg_number = asg_number + 1 #i
        new_asg_name = re.sub(r'\d+', str(new_asg_number), asg_name)

        print(new_asg_name)

        return new_asg_name

        # If we reach this point, we were not able to find a unique ASG name
        # raise Exception('Unable to find unique ASG name')

    def perform_instance_autoscaling_group(self, instance_id):
        try:
            # Returns the name of the Auto Scaling Group for the given EC2 instance ID
            response = self._ec2.describe_instances(InstanceIds=[instance_id])

            for tag in response['Reservations'][0]['Instances'][0]['Tags']:
                if tag['Key'] == 'aws:autoscaling:groupName':
                    print(f"It is already in an ASG with name: {tag['Value']}")
                else:
                    asg_name = self.create_lc_autoscaling_group(instance_id)

            return None
        except Exception as e:
            print(f'Get Instance Autoscaling Group Error: {e}')

    def create_launch_config(self, launch_config_name, ami_id, instance_type, security_groups):
        response = self.autoscaling_client.create_launch_configuration(
            LaunchConfigurationName=launch_config_name,
            ImageId=ami_id,
            InstanceType=instance_type,
            SecurityGroups=security_groups,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {
                        'VolumeSize': 8,
                        'VolumeType': 'gp2'
                    }
                }
            ]
        )

        return response

    def create_asg(self, asg_name, instance_id, min_size, max_size, desired_capacity, launch_config_name, instance):
        response = self.autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchConfigurationName=launch_config_name,
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired_capacity,
            VPCZoneIdentifier=f"{instance['SubnetId']}",
            TargetGroupARNs=[],
            HealthCheckType="EC2",
            HealthCheckGracePeriod=120,
            TerminationPolicies=["Default"],
            NewInstancesProtectedFromScaleIn=True
        )

        return response

    def create_lc_autoscaling_group(self, instance_id, desired_capacity=1, min_size=1, max_size=2):
        asg_name = self.get_asg_name(self.asg_name)

        instance = self._ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        ami_id = instance['ImageId']
        instance_type = instance['InstanceType']
        security_groups = [group['GroupName'] for group in instance['SecurityGroups']]

        launch_config_name = f"lc-for-{asg_name}"
        # Creates a new launch configuration with the given EC2 instance ID as a member
        try:
            get_lc_response = self.create_launch_config(launch_config_name, ami_id, instance_type, security_groups)
        except self.autoscaling_client.exceptions.ClientError as e:
            if "already exists" in str(e).lower():
                logging.error(str(e))

        print("got here")
        described_asg = \
            self.autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        print("described_asg")
        print(described_asg)
        if len(described_asg['AutoScalingGroups']) > 0:
            group = described_asg['AutoScalingGroups'][0]
            _max_size = group['MaxSize']
            current_size = len(group['Instances'])
            if current_size >= _max_size:
                print("Auto Scaling Group has reached maximum capacity")

                # Creates a new Auto Scaling Group with the given EC2 instance ID as a member
                get_asg_response = self.create_asg(asg_name, instance_id, min_size, max_size, desired_capacity,
                                                   launch_config_name, instance)
                return get_asg_response['AutoScalingGroup']['AutoScalingGroupName']
            else:
                print("Auto Scaling Group has not reached maximum capacity yet")

                self.add_instance_to_autoscaling_group(instance_id, asg_name)
                return asg_name
        else:
            print("Auto Scaling Group does not exist")

            # Creates a new Auto Scaling Group with the given EC2 instance ID as a member
            get_asg_response = self.create_asg(asg_name, instance_id, min_size, max_size, desired_capacity,
                                               launch_config_name, instance)

            self.attach_instance_to_autoscaling_group(instance_id, asg_name)
            return asg_name

    def create_new_ec2(self, instance_id):
        # Call the describe_instances API to get the instance metadata
        describe_instance = self._ec2.describe_instances(InstanceIds=[instance_id])
        instance = describe_instance['Reservations'][0]['Instances'][0]
        # Extract the instance metadata from the response
        ami_id = instance['ImageId']
        instance_type = instance['InstanceType']
        security_group_ids = [group['GroupId'] for group in instance['SecurityGroups']]
        subnet_id = instance['SubnetId']
        key_name = describe_instance['Reservations'][0]['Instances'][0]['KeyName']

        response = self._ec2.run_instances(
            ImageId=ami_id,  # replace with your AMI ID
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_name,  # or "ansible"
            SecurityGroupIds=security_group_ids,  # replace with your security group ID(s)
            SubnetId=subnet_id  # replace with your subnet ID
        )

        # The response object returned by run_instances is a dictionary containing information about the launched
        # instance(s), including the instance ID(s), private and public IP addresses, and the instance state.
        return response

    def attach_instance_to_autoscaling_group(self, instance_id, asg_name):
        # Launch a new EC2 instance
        new_ec2 = self.create_new_ec2(instance_id)

        # Wait for the instance to be in the running state
        waiter = self._ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[new_ec2['Instances'][0]['InstanceId']])

        # Attach the given EC2 instance ID to the specified Auto Scaling Group
        response = self.autoscaling_client.attach_instances(
            InstanceIds=[new_ec2['Instances'][0]['InstanceId']],
            AutoScalingGroupName=asg_name
        )

        return response['AutoScalingGroup']['AutoScalingGroupName']

    def add_instance_to_autoscaling_group(self, instance_id, asg_name):
        # Launch a new EC2 instance
        new_ec2 = self.create_new_ec2(instance_id)

        # Wait for the instance to be in the running state
        waiter = self._ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[new_ec2['Instances'][0]['InstanceId']])

        # Adds the given EC2 instance ID to the specified Auto Scaling Group
        response = self.autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        if len(response['AutoScalingGroups']) > 0:
            group = response['AutoScalingGroups'][0]
            instance_ids = [i['InstanceId'] for i in group['Instances']]
            if instance_id not in instance_ids:
                instance_ids.append(instance_id)
                self.autoscaling_client.update_auto_scaling_group(AutoScalingGroupName=asg_name,
                                                                  InstanceIds=instance_ids)

                return response['AutoScalingGroup']['AutoScalingGroupName']
            else:
                print(f"Instance {instance_id} is already a member of {asg_name}")
        else:
            print(f"Auto Scaling Group {asg_name} not found")

    def monitor_cpu_utilization(self, instance_id):
        try:
            # Get the current CPU utilization metrics for the instance
            response = self._ec2.describe_instances(InstanceIds=[instance_id])
            cpu_utilization = response['Reservations'][0]['Instances'][0]['CPUUtilization']['Average']

            # Determine the instance utilization status
            if cpu_utilization > self.scale_out_threshold:
                # Increase the instance capacity
                self.scale_instance(instance_id, self.instance_large_family[0])
            elif cpu_utilization < self.scale_in_threshold:
                # Decrease the instance capacity
                self.scale_instance(instance_id, self.instance_small_family[0])
            else:
                # Do nothing
                pass
        except Exception as e:
            print(f'Error: {e}')

    def scale_instance(self, instance_id, instance_type):
        try:
            # Modify the instance capacity
            self._ec2.modify_instance_attribute(InstanceId=instance_id, Attribute='instanceType', Value=instance_type)
        except Exception as e:
            print(f'Error: {e}')

    def monitor_memory_utilization(self, instance_id):
        try:
            # Get the current memory utilization metrics for the instance
            response = self._ec2.describe_instances(InstanceIds=[instance_id])
            memory_utilization = response['Reservations'][0]['Instances'][0]['MemoryUtilization']

            # Determine the instance memory utilization status
            if memory_utilization > 80:
                # Increase the instance memory
                self._ec2.modify_instance_attribute(InstanceId=instance_id, Attribute='memory', Value='16')
            elif memory_utilization < 70:
                # Increase the instance memory
                self._ec2.modify_instance_attribute(InstanceId=instance_id, Attribute='memory', Value='8')
            else:
                # Do nothing
                pass
        except Exception as e:
            print(f'Error: {e}')

