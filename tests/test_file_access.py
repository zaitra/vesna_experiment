import boto3
import pytest
import typer
import os
from botocore.exceptions import ClientError


def check_remote_access():
    s3 = boto3.client("s3")
    bucket_name = "vesna-camera-control-storage"

    try:
        # Attempt to access the bucket by listing its contents
        s3.list_objects_v2(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            # The bucket does not exist or the user does not have permission to access it
            print(f"Bucket '{bucket_name}' does not exist or access is denied.")
            return False
        elif e.response["Error"]["Code"] == "AccessDenied":
            # The user does not have permission to access the bucket
            print(f"Access to bucket '{bucket_name}' is denied.")
            return False
        else:
            # Handle other exceptions or errors as per your requirements
            print(f"Error occurred while accessing bucket '{bucket_name}': {str(e)}")
            return False


def check_local_access():
    return check_photo() and check_video()


def check_photo():
    valid = True
    path = "sources/BlackMarble_2016_C1_geo.tif"
    return os.path.isfile(path)


def check_video():
    valid = True
    path = "sources/Sahara2EU-002.webm"
    return os.path.isfile(path)


def test_file_access():
    assert check_local_access() or check_remote_access()
