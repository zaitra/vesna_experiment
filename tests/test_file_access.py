import boto3
import pytest
import typer
from typer.testing import CliRunner

from botocore.exceptions import ClientError

import camera_control.__main__ as cc

app = typer.Typer()
app.command()(cc.main)

runner = CliRunner()


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
    return check_run_photo() and check_run_video()


def check_run_photo():
    valid = True
    result = runner.invoke(app, ["test_img_folder_img", "5", "0", "True"])
    valid = valid and result.exit_code == 0
    valid = valid and ("Stopping background" in result.stdout)
    return valid


def check_run_video():
    valid = True
    result = runner.invoke(app, ["test_img_folder_vid", "5", "0", ],)
    valid = valid and result.exit_code == 0
    valid = valid and ("Stopping background" in result.stdout)
    return valid

def test_file_access():
    assert check_local_access() or check_remote_access()
    
