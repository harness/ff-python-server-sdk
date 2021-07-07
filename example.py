from featureflags.evaluations.auth_target import Target
import time

from featureflags.client import CfClient
from featureflags.config import with_base_url, with_events_url, with_stream_enabled
from featureflags.util import log


def main():
    log.debug("Starting example")
    # client = CfClient("7fba0ca2-32d9-4cec-9f9e-5c0fd5d1ee9d")
    client = CfClient('278f5192-1836-4ef6-a9c2-e1cf3c1de9d6')

    target = Target(identifier='harness')
    while True:
        result = client.bool_variation('pytest', target, False)
        log.debug("Result %s", result)
        log.debug(client.get_environment_id())
        time.sleep(10)


if __name__ == "__main__":
    main()
