from featureflags.evaluations.auth_target import Target
import time

from featureflags.client import CfClient
from featureflags.util import log


def main():
    log.debug("Starting example")
    client = CfClient("your SDK key")

    target = Target(identifier='harness')
    while True:
        result = client.bool_variation('test_key', target, False)
        log.debug("Result %s", result)
        time.sleep(10)


if __name__ == "__main__":
    main()
