import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log

## TODO - undo this file
def main():
    log.debug("Starting example")
    api_key = "545535fb-43c0-448d-b57f-498c378c7a80"
    client = CfClient(api_key)

    target = Target(identifier='2')
    target2 = Target(identifier='3')
    target3 = Target(identifier='4')
    target4 = Target(identifier='5')
    while True:
        result = client.bool_variation('flag1', target, False)
        log.debug("Result %s", result)
        result = client.bool_variation('flag1', target2, False)
        log.debug("Result %s", result)
        result = client.bool_variation('flag1', target3, False)
        log.debug("Result %s", result)
        result = client.bool_variation('flag1', target4, False)
        log.debug("Result %s", result)
        time.sleep(10)

if __name__ == "__main__":
    main()
