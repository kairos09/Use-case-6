import boto3
import json
import logging
import os

def lambda_handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    s3 = boto3.resource('s3')
    ec2 = boto3.resource('ec2', region_name='us-east-1')  
    bucket_name = os.environ['BUCKET_NAME']  

    unencrypted_volumes = []
    unattached_volumes = []
    unencrypted_snapshots = []

    try:
        for volume in ec2.volumes.all():
            if volume.encrypted == False:
                unencrypted_volumes.append({"VolumeId": volume.volume_id, "Size": volume.size})
            if len(volume.attachments) == 0:
                unattached_volumes.append({"VolumeId": volume.volume_id, "Size": volume.size})

        for snapshot in ec2.snapshots.filter(OwnerIds=['self']):
            if snapshot.encrypted == False:
                unencrypted_snapshots.append({"SnapshotId": snapshot.snapshot_id, "Size": snapshot.volume_size})

        result = {
            'UnencryptedVolumes': unencrypted_volumes,
            'UnattachedVolumes': unattached_volumes,
            'UnencryptedSnapshots': unencrypted_snapshots
        }

        s3.Object(bucket_name, 'results.json').put(Body=json.dumps(result))
        logger.info('Successfully wrote results to S3')

    except Exception as e:
        logger.error(f'Error occurred: {e}')
        s3.Object(bucket_name, 'log.json').put(Body=json.dumps({"error": str(e)}))
