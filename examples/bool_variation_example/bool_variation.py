import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient
from featureflags.util import log


def main():
    log.debug("Starting example")
    api_key = "545535fb-43c0-448d-b57f-498c378c7a80"
    client = CfClient(api_key)

    # client = CfClient(api_key,
    #                   with_base_url("http://localhost:8000"),
    #                   with_events_url("http://localhost:8000")
    #                   )

    target = Target(identifier='meeee')
    target2 = Target(identifier='meeee3333333')
    target3 = Target(identifier='meeee4444444')
    target4 = Target(identifier='meeee5555555')
    while True:
        result = client.bool_variation('flag1', target, False)
        log.debug("Result %s", result)
        result = client.bool_variation('flag1', target2, False)
        log.debug("Result %s", result)
        result = client.bool_variation('flag1', target3, False)
        log.debug("Result %s", result)
        result = client.bool_variation('flag1', target4, False)
        log.debug("Result %s", result)

        result = client.string_variation('My_string_flag', target2, "hey")
        result = client.string_variation('My_string_flag', target3, "hey")
        result = client.string_variation('My_string_flag', target4, "hey")

        result = client.number_variation('My_cool_number_flag', target2, 0)
        result = client.number_variation('My_cool_number_flag', target3, 0)
        result = client.number_variation('My_cool_number_flag', target4, 0)

        result = client.json_variation('My_JSON_flag', target2, {})
        result = client.json_variation('My_JSON_flag', target3, {})
        result = client.json_variation('My_JSON_flag', target4, {})

        time.sleep(10)

if __name__ == "__main__":
    main()
