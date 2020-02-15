#!/usr/local/bin/python3
import re

from prettytable import PrettyTable
import boto3
import click
from botocore.exceptions import ClientError
import sys


ec2 = None

@click.group()
def cli():
    '''
    Helper commands for volume management.
    '''
    pass

def print_debug(debug,message):
    if (debug):
      print (message)

@cli.command()
@click.argument('regions', nargs=-1)
@click.option('-A','--all', default = False,is_flag = True, help = "Check on all regions")
@click.option('-d','--debug', default = False, is_flag= True, help = "Show all messages for debug")
def volumes_available(regions, all, debug):
    '''
    Find available volumes.
    '''
    global ec2

    if (all):
        try:
            ec2 = boto3.client('ec2')
            print_debug(debug,"Listing resources on all regions. Be Patient.")
            regions = list_all_regions()
        except Exception as e:
            print (e)
            sys.exit(1)
    elif (len(regions) == 0):
        click.echo('Add at least one region')

    for region in regions:
        try:
            ec2 = boto3.client('ec2', region_name=region)
        except Exception as e:
            print (e)
            sys.exit(1)

        table = PrettyTable(['id', 'create_time', 'status', 'size', 'snapshot_id', 'snapshot_exists'])
        for volume in get_available_volumes():
                table.add_row([volume['id'], volume['create_time'], volume['status'],volume['size'], volume['snapshot_id'],volume['snapshot_exists']   ])

        if (len(list(table)) == 0):
            print_debug(debug,f'There is no available volumes on the region: {region}')
        else:
            print ('\b')
            print ('-----------------------------')
            print (f"Resources on region {region}")
            print (table)


def list_all_regions():
    '''
    Get a list of all available regions
    '''
    list_all_regions = []

    response = ec2.describe_regions()

    for region in response['Regions']:
        list_all_regions.append(region['RegionName'])
    return list_all_regions

         
def get_available_volumes():
    '''
    Get all volumes in available state.
    '''
    for volume in ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])['Volumes']:
        yield {
            'id': volume['VolumeId'],
            'create_time': volume['CreateTime'],
            'status': volume['State'],
            'size': volume['Size'],
            'snapshot_id': volume['SnapshotId'],
            'snapshot_exists': str(check_snapshot_exists(volume['SnapshotId']))
        }


def check_snapshot_exists(snapshot_id):
    '''
    Verifies if a snapshot exists.
    '''
    if not snapshot_id:
        return ''
    try:
        ec2.describe_snapshots(SnapshotIds=[snapshot_id])
        return True
    except ClientError:
        return False

if __name__ == '__main__':
    cli()   