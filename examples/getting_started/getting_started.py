from featureflags.client import CfClient
from featureflags.config import *
from featureflags.evaluations.auth_target import Target
from featureflags.util import log
import os
import time


# API Key
apiKey = os.getenv('FF_API_KEY', "")

# Flag Name
flagName = os.getenv('FF_FLAG_NAME', "harnessappdemodarkmode")

def main():
    log.info("Harness SDK Getting Started")
    # Create a Feature Flag Client
    client = CfClient(apiKey)


    # Create a target (different targets can get different results based on rules)
    target = Target(identifier='pythonSDK', name="PythonSDK", attributes={"location": "emea"})

    # Loop forever reporting the state of the flag
    while True:
        result = client.bool_variation(flagName, target, False)
        log.info("Flag variation %s", result)
        time.sleep(10)
           
    close()


if __name__ == "__main__":
    main()
