import logging
import os
import time

from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log

api_key = os.getenv('FF_API_KEY', "")


def main():
    log.setLevel(logging.INFO)
    api_key = "Your API Key"

    # Create a Feature Flag Client
    client = CfClient(api_key)
    client.wait_for_initialization()

    # Create a target (different targets can get different results based on
    # rules that you add in the UI).
    target = Target(identifier='HT_1', name="Harness_Target_1",
                    attributes={"location": "emea"})

    # Loop forever reporting the state of the flag.  If there is an error
    # the default value will be returned
    while True:
        result = client.bool_variation('harnessappdemodarkmode', target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)


if __name__ == "__main__":
    main()
