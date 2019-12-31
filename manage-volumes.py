#!/usr/local/bin/python3
import csv
import re
from collections import OrderedDict
from pprint import pprint
from prettytable import PrettyTable

import boto3
import click
from botocore.exceptions import ClientError


ec2 = None

@click.group()
def cli():
    '''
    Helper commands for volume management.
    '''
    pass


@cli.command()
@click.argument('regions', nargs=-1)
def volumes_available(regions):
    '''
    Find unreferenced snapshots.
    '''
    global ec2
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        table = PrettyTable(['id', 'create_time', 'status', 'size', 'snapshot_id', 'snapshot_exists'])
        for volume in get_available_volumes():
            table.add_row([volume['id'], volume['create_time'], volume['status'],volume['size'], volume['snapshot_id'],volume['snapshot_exists']   ])
        print (table)

         
def get_available_volumes():
    '''
    Get all volumes in 'available' state. (Volumes not attached to any instance)
    '''
    for volume in ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])['Volumes']:
        yield {
            'id': volume['VolumeId'],
            'create_time': volume['CreateTime'],
            'status': volume['State'],
            'size': volume['Size'],
            'snapshot_id': volume['SnapshotId'],
            'snapshot_exists': str(snapshot_exists(volume['SnapshotId']))
        }


def snapshot_exists(snapshot_id):
    if not snapshot_id:
        return ''
    try:
        ec2.describe_snapshots(SnapshotIds=[snapshot_id])
        return True
    except ClientError:
        return False

if __name__ == '__main__':
    cli()