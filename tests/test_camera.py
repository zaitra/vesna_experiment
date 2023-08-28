import cv2
import EasyPySpin
import typer
from typer.testing import CliRunner


def use_camera():
    cap = EasyPySpin.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 10)
    cap.release()


app = typer.Typer()
app.command()(use_camera)

runner = CliRunner()


def test_camera():
    result = runner.invoke(app)

    # Check whether connection is proper based on warning that only occurs when the connection is bad
    assert "EasyPySpinWarning: AcquisitionFrameRate" not in result.stdout
    # Check whether there is access to a camera
    assert result.exit_code == 0
