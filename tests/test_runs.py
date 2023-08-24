import boto3
import pytest
import typer
from typer.testing import CliRunner

from botocore.exceptions import ClientError

import camera_control.__main__ as cc

app = typer.Typer()
app.command()(cc.main)

runner = CliRunner()


def check_run_photo():
    valid = True
    result = runner.invoke(app, ["test_img_folder_img", "5", "0", "True"])
    valid = valid and result.exit_code == 0
    valid = valid and ("Stopping background" in result.stdout)
    return valid


def check_run_video():
    valid = True
    result = runner.invoke(
        app,
        [
            "test_img_folder_vid",
            "5",
            "0",
        ],
    )
    valid = valid and result.exit_code == 0
    valid = valid and ("Stopping background" in result.stdout)
    return valid


def test_runs():
    assert check_run_photo() and check_run_video()
