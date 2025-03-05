import boto3

ec2 = boto3.client('ec2')
def lambda_handler(event, context):
    instance_response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    active_instance_ids = set()
    for reservation in instance_response['Reservations']:
        for instance in reservation['Instances']:
            active_instance_ids.add(instance['InstanceId'])

    print(f"Active Running Instances: {active_instance_ids}")

    snapshots = []
    
    for instance_id in active_instance_ids:
        # Get all attached volumes
        volume_response = ec2.describe_instances(InstanceIds=[instance_id])
        volumes = [vol['Ebs']['VolumeId'] for res in volume_response['Reservations'] for inst in res['Instances'] for vol in inst['BlockDeviceMappings']]
        
        for volume_id in volumes:
            # Create snapshot
            snapshot = ec2.create_snapshot(
                VolumeId=volume_id,
            )
            
            snapshots.append(snapshot['SnapshotId'])
            print(f"Created snapshot {snapshot['SnapshotId']} for volume {volume_id} of instance {instance_id}")

    return {
        'statusCode': 200,
        'body': f"Created snapshots: {snapshots}"
    }
