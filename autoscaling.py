import boto3

# Configuration
REGION = 'us-east-1'
LAUNCH_TEMPLATE_NAME = 'my-launch-template'
ASG_NAME = 'my-auto-scaling-group'
TARGET_GROUP_ARN = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-target-group/abcd1234efgh5678'
VPC_ZONE_IDENTIFIER = 'subnet-xxxxxxx,subnet-yyyyyyy'

MIN_INSTANCES = 2
MAX_INSTANCES = 5
DESIRED_CAPACITY = 2
INSTANCE_TYPE = 't3.micro'
AMI_ID = 'ami-0abcdef1234567890'
KEY_NAME = 'my-keypair'

autoscaling = boto3.client('autoscaling', region_name=REGION)
ec2 = boto3.client('ec2', region_name=REGION)

def create_launch_template():
    try:
        response = ec2.create_launch_template(
            LaunchTemplateName=LAUNCH_TEMPLATE_NAME,
            LaunchTemplateData={
                'ImageId': AMI_ID,
                'InstanceType': INSTANCE_TYPE,
                'KeyName': KEY_NAME,
                'SecurityGroupIds': ['sg-xxxxxxxx'],
                'UserData': '',
                'TagSpecifications': [{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'AutoScalingInstance'}]
                }]
            }
        )
        print(f"✅ Launch Template '{LAUNCH_TEMPLATE_NAME}' created.")
    except ec2.exceptions.ClientError as e:
        if 'InvalidLaunchTemplateName.AlreadyExistsException' in str(e):
            print(f"ℹ️ Launch Template '{LAUNCH_TEMPLATE_NAME}' already exists.")
        else:
            raise e

def create_auto_scaling_group():
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName=ASG_NAME,
        LaunchTemplate={
            'LaunchTemplateName': LAUNCH_TEMPLATE_NAME,
            'Version': '$Latest'
        },
        MinSize=MIN_INSTANCES,
        MaxSize=MAX_INSTANCES,
        DesiredCapacity=DESIRED_CAPACITY,
        TargetGroupARNs=[TARGET_GROUP_ARN],
        VPCZoneIdentifier=VPC_ZONE_IDENTIFIER,
        Tags=[{
            'Key': 'Name',
            'Value': 'AutoScalingGroupInstance',
            'PropagateAtLaunch': True
        }]
    )
    print(f"✅ Auto Scaling Group '{ASG_NAME}' created.")

def create_scaling_policy():
    autoscaling.put_scaling_policy(
        AutoScalingGroupName=ASG_NAME,
        PolicyName='cpu-scale-out',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 50.0,  # Target CPU utilization %
            'Cooldown': 300
        }
    )
    print("✅ Auto Scaling Policy applied (target CPU utilization at 50%).")

def main():
    create_launch_template()
    create_auto_scaling_group()
    create_scaling_policy()
    print("🎉 Auto Scaling setup complete!")

if __name__ == '__main__':
    main()
