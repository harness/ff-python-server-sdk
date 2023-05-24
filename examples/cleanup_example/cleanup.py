import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log

def main():
    log.debug("Starting example")
    api_key = "Your API key"
    client = CfClient(api_key)

    target = Target(identifier='HT_1', name="Harness_Target_1", attributes={"location": "emea"})

    for x in range(10):
        result = client.bool_variation('harnessappdemodarkmode', target, False)
        log.debug("Result %s", result)
        time.sleep(10)

    client.close()

if __name__ == "__main__":
    main()
