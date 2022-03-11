import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log
from featureflags.config import with_base_url
from featureflags.config import with_events_url


def main():
    log.debug("Starting example")
    api_key = "Your API key"
    client = CfClient(api_key,
                      with_base_url("https://config.ff.harness.io/api/1.0"),
                      with_events_url("https://events.ff.harness.io/api/1.0"))

    target = Target(identifier='harness')

    while True:
        result = client.bool_variation('your_flag_identifier', target, False)
        log.debug("Result %s", result)
        time.sleep(10)

if __name__ == "__main__":
    main()
