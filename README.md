Python SDK For Harness Feature Flags
========================

[![pypi](https://img.shields.io/pypi/v/harness-featureflags.svg)](https://pypi.python.org/pypi/harness-featureflags)

## Table of Contents
**[Intro](#Intro)**<br>
**[Requirements](#Requirements)**<br>
**[Quickstart](#Quickstart)**<br>
**[Further Reading](docs/further_reading.md)**<br>
**[Build Instructions](docs/build.md)**<br>


## Intro

Use this README to get started with our Feature Flags (FF) SDK for Python. This guide outlines the basics of getting started with the SDK and provides a full code sample for you to try out. 
This sample doesn’t include configuration options, for in depth steps and configuring the SDK, for example, disabling streaming or using our Relay Proxy, see the  [Python SDK Reference](https://ngdocs.harness.io/article/hwoxb6x2oe-python-sdk-reference).

For a sample FF Python SDK project, see our test [test python project](examples/getting_started/getting_started.py).

![FeatureFlags](https://github.com/harness/ff-python-server-sdk/raw/main/docs/images/ff-gui.png)

## Requirements

[Python 3.7](https://www.python.org/downloads/) or newer (python --version)<br>
[pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#id12)<br>
<br>
[For Mac users](https://opensource.com/article/19/5/python-3-default-mac) if you don't already have pyenv or something similar installed for managing python version<br>


## Quickstart
To follow along with our test code sample, make sure you’ve:

- [Created a Feature Flag on the Harness Platform](https://ngdocs.harness.io/article/1j7pdkqh7j-create-a-feature-flag) called harnessappdemodarkmode
- [Created a server SDK key and made a copy of it](https://ngdocs.harness.io/article/1j7pdkqh7j-create-a-feature-flag#step_3_create_an_sdk_key)
- 
### Install the SDK
Install the python SDK using pip
```python
python -m pip install harness-featureflags
```

### Code Sample
The following is a complete code example that you can use to test the `harnessappdemodarkmode` Flag you created on the Harness Platform. When you run the code it will:
- Connect to the FF service.
- Report the value of the Flag every 10 seconds until the connection is closed. Every time the harnessappdemodarkmode Flag is toggled on or off on the Harness Platform, the updated value is reported. 
- Close the SDK.

```python
from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log
import os
import time

# API Key
apiKey = os.getenv('FF_API_KEY', "changeme")

# Flag Name
flagName = os.getenv('FF_FLAG_NAME', "harnessappdemodarkmode")

def main():    
    # Create a Feature Flag Client
    client = CfClient(apiKey)

    # Create a target (different targets can get different results based on rules.  This include a custom attribute 'location')
    target = Target(identifier='pythonSDK', name="PythonSDK", attributes={"location": "emea"})

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation(flagName, target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)

    close()


if __name__ == "__main__":
    main()
```

### Running the example

```bash
$ export FF_API_KEY=<your key here>
$ python3 examples/getting_started/getting_started.py
```

### Running the example with Docker
If you dont have the right version of python installed locally, or dont want to install the dependancies you can
use docker to quickly get started

```bash
# Install the package
docker run -v $(pwd):/app -w /app python:3.7-slim python -m pip install -t ./local  harness-featureflags

# Run the script
docker run  -e PYTHONPATH=/app/local -e FF_API_KEY=$FF_API_KEY -v $(pwd):/app -w /app python:3.7-slim python examples/getting_started/getting_started.py
```

### Additional Reading

For further examples and config options, see the [Python SDK Reference](https://ngdocs.harness.io/article/hwoxb6x2oe-python-sdk-reference).

For more information about Feature Flags, see our [Feature Flags documentation](https://ngdocs.harness.io/article/0a2u2ppp8s-getting-started-with-feature-flags).

-------------------------
[Harness](https://www.harness.io/) is a feature management platform that helps teams to build better software and to
test features quicker.

-------------------------

