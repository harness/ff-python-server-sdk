Harness Feature Flag Python SDK
========================

[![pypi](https://img.shields.io/pypi/v/harness-featureflags.svg)](https://pypi.python.org/pypi/harness-featureflags)

## Table of Contents
**[Intro](#Intro)**<br>
**[Requirements](#Requirements)**<br>
**[Quickstart](#Quickstart)**<br>
**[Advanced Configuration](docs/advanced.md)**<br>
**[Build Instructions](docs/build.md)**<br>


## Intro

Harness Feature Flags (FF) is a feature management solution that enables users to change the software’s functionality, without deploying new code. FF uses feature flags to hide code or behaviours without having to ship new versions of the software. A feature flag is like a powerful if statement.
* For more information, see https://harness.io/products/feature-flags/
* To read more, see https://ngdocs.harness.io/category/vjolt35atg-feature-flags
* To sign up, https://app.harness.io/auth/#/signup/

## Requirements

[Python 3.7](https://www.python.org/downloads/) or newer (python --version)<br>
[pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#id12)

## Quickstart

### Install

python -m pip install harness-featureflags

### Sample Client

```python
import time

from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log


def main():
    # Create a Feature Flag Client
    client = CfClient("c9b3f14f-6336-4d23-83b4-73f29d1ebefa",
                      with_base_url("https://config.feature-flags.uat.harness.io/api/1.0"),
                      with_events_url("https://event.feature-flags.uat.harness.io/api/1.0"))

    # Create a target (different targets can get different results based on rules)
    target = Target(identifier='mytarget', name="FriendlyName")

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation('harnessappdemodarkmode', target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)


if __name__ == "__main__":
    main()
```
### Adding SDK key
Log into Feature flags UI > environments > select/create your environment > select add key

### Getting the Variation for your flag 

### To Run
`python3 <pathto your client>/<yourclient.py>`

    
**[Advanced Configuration](docs/advanced.md)**<br>
**[Build Instructions](docs/build.md)**<br>


## Intro
## Requirements
## Quickstart

-------------------------
[Harness](https://www.harness.io/) is a feature management platform that helps teams to build better software and to
test features quicker.

-------------------------
