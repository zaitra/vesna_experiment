import typer
from typer.testing import CliRunner

import camera_control.__main__ as cc

app = typer.Typer()
app.command()(cc.main)

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert "Usage" in result.stdout
    assert "Arguments" in result.stdout
    assert "Options" in result.stdout
