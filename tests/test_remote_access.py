import boto3
import pytest
import typer
from botocore.exceptions import ClientError


def test_bucket_access():
    s3 = boto3.client("s3")
    bucket_name = "vesna-camera-control-storage"

    try:
        # Attempt to access the bucket by listing its contents
        s3.list_objects_v2(Bucket=bucket_name)
        assert True
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            # The bucket does not exist or the user does not have permission to access it
            assert False, f"Bucket '{bucket_name}' does not exist or access is denied."
        elif e.response["Error"]["Code"] == "AccessDenied":
            # The user does not have permission to access the bucket
            assert False, f"Access to bucket '{bucket_name}' is denied."
        else:
            # Handle other exceptions or errors as per your requirements
            assert (
                False
            ), f"Error occurred while accessing bucket '{bucket_name}': {str(e)}"
