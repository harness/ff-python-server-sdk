import logging
import time

from featureflags.evaluations.auth_target import Target
from featureflags.client import CfClient, FeatureFlagType
from featureflags.util import log


def main():
    log.setLevel(logging.INFO)
    log.info("Starting example")
    api_key = "your_api_key"
    client = CfClient(api_key)
    # Don't continue until all flags and groups have been loaded into the
    # cache.
    log.info("Waiting to load all flags and groups before proceeding")
    client.wait_for_initialization()

    target = Target(identifier='harness')

    flag_identifier = 'any_flag'

    # Get the flag type
    flag_type = client.get_flag_type(flag_identifier)
    log.info("Flag '%s' is of type '%s'", flag_identifier, flag_type)

    # Ensure the right variation method is called based on the flag type
    variation_methods = {
        FeatureFlagType.BOOLEAN: lambda: client.bool_variation(flag_identifier, target, False),

        FeatureFlagType.STRING: lambda: client.string_variation(flag_identifier, target, "default"),

        FeatureFlagType.FLOAT_OR_INT: lambda: client.int_or_float_variation(flag_identifier, target, 3.2),

        FeatureFlagType.JSON: lambda: client.json_variation(flag_identifier, target, {}),

        # If the flag cannot be found, log an error
        FeatureFlagType.FLAG_NOT_FOUND: lambda: log.error("Flag %s was not found", flag_identifier)
    }

    while True:
        result = variation_methods[flag_type]()
        log.info("Result for flag type '%s' is %s", flag_type, result)
        time.sleep(10)


if __name__ == "__main__":
    main()
