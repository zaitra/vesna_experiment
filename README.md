# Camera control script for Vesna Experiment

## Setup

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

