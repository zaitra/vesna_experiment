# Camera control script for Vesna Experiment

# vesna-datagen

Python package for generating dataset experiments for Vesna.

### Experiment outline

Connect the camera to your machine and aim it at the screen. Run the package with preferred or default parameters. After the program is done running you'll find the footage captured by the camera in the folder 'images/target_folder_name_here'

## Setup

### Dependencies

The only dependency so far is the Spinnaker SDK Python wheel. It can be found [here](https://www.flir.eu/products/spinnaker-sdk/?vertical=machine+vision&segment=iis).

You should preferably look for "spinnaker_python-3.1.0.79-cp310-cp310-win_amd64.whl", and place it in a dependencies/PySpin/ folder in the root of the project.

#### Optional alternative setup (may be outdated)

1. To install SpinMaked SDK, download archives for both system package and Python module from https://flir.app.boxcn.net/v/SpinnakerSDK?pn=Spinnaker+SDK&vn=Spinnaker_SDK 
Note that the latest supported Ubuntu is 20, so be carefull when selecting OS for RPI or other Linux machine.


2. Install missing dependencies
```
sudo apt install qt5-default libgomp1
```

3. Install SpinMaker SDK
```
cd spinnaker-2.7.0.128-amd64/ 
sudo sh install_spinnaker.sh
```

4. Install Python wheel from the second archive.
```
pip install --user spinnaker_python-2.7.0.128-cp38-cp38-linux_x86_64.whl 
```

More detailed information are in the README in the archive.

### Installation
All remaining necessary libraries should be fetchable by [poetry](https://python-poetry.org/).

To get poetry, you can install it by pip (Make sure it is separate from the main environment):

Then, install the libraries as described in pyproject.toml by:

	poetry install

## How to run

### Tests

Before running the experiment, it is recommended to run the tests through:

	poetry run pytest

The tests will check whether the FLIR camera is connected properly, whether user has access to the right bucket for streaming source backgrounds, and some basic unit tests.

If all tests pass, then everything should be setup correctly.

### Main

For a full list of arguments/parameters:

	python -m src.camera_control --help

Two ways to run the program:

	python -m src.camera_control 'args'

The above may require to install all necessary libraries to your machine. If you prefer to conveniently use the virtual environment created by poetry with all the necessary dependencies, use:

	poetry run main
