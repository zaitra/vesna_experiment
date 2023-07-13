# vesna-datagen

Python package for generating dataset experiments for Vesna.

### Experiment outline

Connect the camera to your machine and aim it at the screen. Run the package with preferred or default parameters. After the program is done running you'll find the footage captured by the camera in the folder 'images/target_folder_name_here'

## Setup

### Dependencies

The only dependency so far is the Spinnaker SDK Python wheel. It can be found [here](https://www.flir.eu/products/spinnaker-sdk/?vertical=machine+vision&segment=iis).

### Installation
All libraries should be fetchable by [poetry](https://python-poetry.org/).

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

Two ways to run an experiment:

	python -m src.camera_control 'args'

The above may require to install all necessary libraries to your machine. If you prefer to conveniently use the virtual environment created by poetry with all the necessary dependencies, use:

	poetry run main
