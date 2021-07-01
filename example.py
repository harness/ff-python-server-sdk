from featureflags.evaluations.auth_target import Target
import time

from featureflags.client import CfClient
from featureflags.config import with_stream_enabled
from featureflags.util import log


def main():
    log.debug("Starting example")
    client = CfClient("7fba0ca2-32d9-4cec-9f9e-5c0fd5d1ee9d")

    target = Target(identifier='harness')
    while True:
        result = client.bool_variation('pytest', target, False)
        log.debug("Result %s", result)
        log.debug(client.get_environment_id())
        time.sleep(10)


if __name__ == "__main__":
    main()
