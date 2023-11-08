import logging
import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log


def main():
    log.setLevel(logging.INFO)
    log.info("Starting example")
    api_key = "Your API Key"
    client = CfClient(api_key)

    target = Target(identifier='HT_1', name="Harness_Target_1",
                    attributes={"location": "emea"})

    while True:
        result = client.bool_variation('identifier_of_your_bool_flag', target,
                                       False)
        log.info("Result %s", result)
        time.sleep(10)


if __name__ == "__main__":
    main()
