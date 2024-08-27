import logging
import time

from featureflags.config import with_httpx_args, with_base_url
from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log


def main():
    log.setLevel(logging.INFO)
    log.info("Starting example")
    api_key = "Your API key"

    # Using the httpx proxies option.
    # Ensure you supply a valid httpx option. if you supply an option that
    # doesn't exist in `httpx` the SDK will fail to initialize with `got an
    # unexpected keyword argument`
    client = CfClient(api_key,
                      with_httpx_args({'proxies': 'http://localhost:8888'}))

    client.wait_for_initialization()

    target = Target(identifier='HT_1', name="Harness_Target_1",
                    attributes={"location": "emea"})

    while True:
        result = client.bool_variation('identifier_of_your_bool_flag', target,
                                       False)
        log.info("Result %s", result)
        time.sleep(10)


if __name__ == "__main__":
    main()
