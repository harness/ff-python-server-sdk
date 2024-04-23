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
flagName = os.getenv('FF_FLAG_NAME', "test")

configURL = os.environ.get("FF_CONFIG_URL", "https://ffserver:8000/api/1.0")
eventsURL = os.environ.get("FF_CONFIG_URL", "https://ffserver:8001/api/1.0")


def main():
    log.setLevel(logging.INFO)
    log.info("Harness SDK Getting Started")
    # Create a Feature Flag Client

    client = CfClient(api_key,
                      with_base_url(configURL),
                      with_events_url(eventsURL),
                      with_tls_trusted_cas_file(
                          "/Users/andrewbell/dev/andyb-tls-scripts/sdk"
                          "/examples_from_scratch/python-sdk-from-scratch/CA"
                          ".crt"))
    client.wait_for_initialization()

    # Create a target (different targets can get different results based on
    # rules)
    target = Target(identifier='HT_1', name="Harness_Target_1",
                    attributes={"location": "emea"})

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation(flagName, target, False)
        log.info("%s flag variation %s", flagName, result)
        time.sleep(10)


if __name__ == "__main__":
    main()
