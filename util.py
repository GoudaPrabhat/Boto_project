import boto3
import datetime

# Initialize AWS clients (Set the correct region)
cloudwatch = boto3.client("cloudwatch")
ec2 = boto3.client("ec2")

def utilcheck(instance_id):
    """Fetches the CPU utilization of an EC2 instance from CloudWatch."""
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
        EndTime=datetime.datetime.utcnow(),
        Period=300,  # 5-minute interval
        Statistics=["Average"],
        Unit="Percent",
    )
    datapoints = response.get("Datapoints", [])
    return datapoints[0]["Average"] if datapoints else None

def low_util_inst():
    """Finds running EC2 instances with CPU utilization <10% and tags them."""
    instances = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
    low_util_instances = []

    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            cpu_util = utilcheck(instance_id)

            if cpu_util is not None and cpu_util < 10:
                low_util_instances.append(instance_id)
                print(f"Instance {instance_id} has low CPU utilization: {cpu_util:.2f}%")
    
    # Apply "LowUtilization" tag to instances below 10% CPU
    if low_util_instances:
        ec2.create_tags(
            Resources=low_util_instances,
            Tags=[{"Key": "Utilization", "Value": "LowUtilization"}],
        )
        print(f"Tagged instances: {low_util_instances}")

    return low_util_instances  # Fix: Return actual list, not function reference

def terminateInst(instance_ids):
    """Terminates EC2 instances that are tagged as 'LowUtilization'."""
    if instance_ids:
        ec2.terminate_instances(InstanceIds=instance_ids)
        print(f"Terminated instances: {instance_ids}")
    else:
        print("No low utilization instances found.")

def lambda_handler(event, context):
    """AWS Lambda Entry Point: Checks for low-utilization EC2 instances & terminates them."""
    low_util_instances = low_util_inst()  # Fix: Store the returned instance list
    terminateInst(low_util_instances)  # Fix: Pass the correct instance list

    return {"statusCode": 200, "body": "EC2 Low Utilization Check & Termination Completed"}
