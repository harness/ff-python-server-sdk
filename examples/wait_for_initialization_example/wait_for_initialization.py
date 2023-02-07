import time

from featureflags.config import with_base_url, with_events_url
from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log


def main():
    log.debug("Starting example")
    api_key = "Your API Key"
    client = CfClient(api_key)
    # Don't continue until all flags and groups have been loaded into the cache.
    log.debug("Waiting to load all flags and groups before proceeding")
    client.wait_for_initialization()

    #  If required you can check the initialized status of the Client at anytime
    log.debug("Client is_initialized status is %s", client.is_initialized())
    target = Target(identifier='harness')

    while True:
        result = client.bool_variation('identifier_of_your_bool_flag', target, False)
        log.debug("Result %s", result)
        time.sleep(10)


if __name__ == "__main__":
    main()
