import logging

from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log
import os
import time


# API Key
api_key = os.getenv('FF_API_KEY', "")

# Flag Name
flagName = os.getenv('FF_FLAG_NAME', "harnessappdemodarkmode")

def main():
    log.setLevel(logging.INFO)
    log.info("Harness SDK Getting Started")
    # Create a Feature Flag Client
    client = CfClient(api_key)
    client.wait_for_initialization()


    # Create a target (different targets can get different results based on rules)
    target = Target(identifier='HT_1', name="Harness_Target_1", attributes={"location": "emea"})

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation(flagName, target, False)
        log.info("%s flag variation %s", flagName, result)
        time.sleep(10)
           


if __name__ == "__main__":
    main()
