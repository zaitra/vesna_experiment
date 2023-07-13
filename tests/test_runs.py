import typer
from typer.testing import CliRunner
import camera_control.__main__ as cc

app = typer.Typer()
app.command()(cc.main)

runner = CliRunner()


def test_run_photo():
    result = runner.invoke(app, ["test_img_folder_img", "5", "0", "True"])
    assert result.exit_code == 0
    assert "Stopping background" in result.stdout


def test_run_video():
    result = runner.invoke(
        app,
        [
            "test_img_folder_vid",
            "5",
            "0",
        ],
    )
    assert result.exit_code == 0
    assert "Stopping background" in result.stdout
