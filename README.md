Harness Feature Flag Python SDK
========================

[![pypi](https://img.shields.io/pypi/v/harness-featureflags.svg)](https://pypi.python.org/pypi/harness-featureflags)

## Table of Contents
**[Intro](#Intro)**<br>
**[Requirements](#Requirements)**<br>
**[Quickstart](#Quickstart)**<br>
**[Further Reading](docs/further_reading.md)**<br>
**[Build Instructions](docs/build.md)**<br>


## Intro

Harness Feature Flags (FF) is a feature management solution that enables users to change the software’s functionality, without deploying new code. FF uses feature flags to hide code or behaviours without having to ship new versions of the software. A feature flag is like a powerful if statement.
* For more information, see https://harness.io/products/feature-flags/
* To read more, see https://ngdocs.harness.io/category/vjolt35atg-feature-flags
* To sign up, https://app.harness.io/auth/#/signup/

![FeatureFlags](https://github.com/harness/ff-python-server-sdk/raw/main/docs/images/ff-gui.png)

## Requirements

[Python 3.7](https://www.python.org/downloads/) or newer (python --version)<br>
[pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#id12)<br>
<br>
[For Mac users](https://opensource.com/article/19/5/python-3-default-mac) if you don't already have pyenv or something similar installed for managing python version<br>


## Quickstart
The Feature Flag SDK provides a client that connects to the feature flag service, and fetches the value
of featue flags.   The following section provides an example of how to install the SDK and initalize it from
an application.
This quickstart assumes you have followed the instructions to [setup a Feature Flag project and have created a flag called `simpleboolflag` and created a server API Key](https://ngdocs.harness.io/article/1j7pdkqh7j-create-a-feature-flag#step_1_create_a_project).

### Install the SDK
Install the python SDK using pip
```python
python -m pip install harness-featureflags
```

### Initialize the SDK
To intialize the SDK you need to provide an API Key.
```python
    client = CfClient("c9b3f14f-6336-4d23-83b4-73f29d1ebefa")
```

### Setup a Target
The client will evaluate a flag and return the value.  A target must be provided for the evaluation.
If no special [target rules](https://ngdocs.harness.io/article/xf3hmxbaji-targeting-users-with-flags) have been added in the feature flag service for the target, then the flag defaults will be returned. 
To create a target do the following - provide an identifier and (optionally) a friendly name.   When the client authenticates with the feature flag service it will automatically register the target if it doesn't exist:
```python
    target = Target(identifier='mytarget', name="FriendlyName")
```



### Evaluate the Flag
You can now call one of the evaluate functions, to get the value of a flag.   Incase there is an error you
can specify the default that should be returned.
```python
result = client.bool_variation('simpleboolflag', target, False)
```

### Working Example
Here is a complete example that will connect and report the flag value every 10 seconds until the connection is clsed.  Any time a flag is 
toggled from the feature flag service you will receive the updated value.

```python
import time

from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log


def main():
    # Create a Feature Flag Client
    client = CfClient("c9b3f14f-6336-4d23-83b4-73f29d1ebeeb",
                      with_base_url("https://config.ff.harness.io/api/1.0"),
                      with_events_url("https://events.ff.harness.io/api/1.0"))

    # Create a target (different targets can get different results based on rules)
    target = Target(identifier='mytarget', name="FriendlyName")

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation('harnessappdemodarkmode', target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)
           
    close()


if __name__ == "__main__":
    main()
```

### Running the example
You can save the above to a file called `sdk_sample.py` and run with

```bash
$ python sdk_sample.py
```

### Additional Reading

Further examples and config options are in the further reading section:

[Further Reading](docs/further_reading.md)


-------------------------
[Harness](https://www.harness.io/) is a feature management platform that helps teams to build better software and to
test features quicker.

-------------------------
