from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log
import os
import time

# API Key
apiKey = os.getenv('FF_API_KEY', "c9b3f14f-6336-4d23-83b4-73f29d1ebeeb")

# Flag Name
flagName = os.getenv('FF_FLAG_NAME', "harnessappdemodarkmode")

def main():
    # Create a Feature Flag Client
    client = CfClient(apiKey)

    # Create a target (different targets can get different results based on rules)
    target = Target(identifier='mytarget', name="FriendlyName", attributes={"location": "emea"})

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation(flagName, target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)
           
    close()


if __name__ == "__main__":
    main()
