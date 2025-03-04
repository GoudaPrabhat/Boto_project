import boto3


def lambda_handler(event, context):
    client = boto3.client('ec2')
    response = client.describe_snapshots(OwnerIds=['self'])


    instance_response = client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    active_instance_ids = set()


    for reservation in instance_response['Reservations']:
        for instance in reservation['Instances']:
            active_instance_ids.add(instance['InstanceId'])
    
    for snapshot in response['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot['VolumeId']

    if not volume_id:

        client.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Deleted snapshot {snapshot_id} as it is not associated with any volume.")
    else:
        try:
            volume_response = client.describe_volumes(VolumeIds=[volume_id])
            if not volume_response['Volumes'][0]['Attachments']:
                client.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot {snapshot_id} as it is not associated with any instance.")
        except client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                client.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot {snapshot_id} as the associated volume {volume_id} was not found.")
            else:
                raise e