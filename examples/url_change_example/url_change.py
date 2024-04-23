import logging
import os
import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log
from featureflags.config import with_base_url
from featureflags.config import with_events_url


def main():
    log.setLevel(logging.INFO)
    log.info("Starting example")
    api_key = os.getenv('FF_API_KEY', "")
    client = CfClient(api_key,
                      with_base_url("https://config.ff.harness.io/api/1.0"),
                      with_events_url("https://events.ff.harness.io/api/1.0"))
    client.wait_for_initialization()

    target = Target(identifier='HT_1', name="Harness_Target_1", attributes={"location": "emea"})

    while True:
        result = client.bool_variation('harnessappdemodarkmode', target, False)
        log.info("Result %s", result)
        time.sleep(10)

if __name__ == "__main__":
    main()
