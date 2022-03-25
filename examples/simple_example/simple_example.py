import time

from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log


def main():
    # Create a Feature Flag Client
    client = CfClient("c9b3f14f-6336-4d23-83b4-73f29d1ebeeb")

    # Create a target (different targets can get different results based on rules that you add in the UI).  
    target = Target(identifier='mytarget', name="FriendlyName")

    # Loop forever reporting the state of the flag.  If there is an error the default value will be returned
    while True:
        result = client.bool_variation('simpleboolflag', target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)
           
    close()


if __name__ == "__main__":
    main()
