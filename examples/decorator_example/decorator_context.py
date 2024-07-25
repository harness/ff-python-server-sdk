import functools
from contextlib import contextmanager
from featureflags.client import CfClient, FeatureFlagType
from featureflags.evaluations.auth_target import Target

# Global context to store the ff_client and eval_target
context = {}


@contextmanager
def feature_flag_context(client: CfClient, target: Target):
    context['ff_client'] = client
    context['eval_target'] = target
    try:
        yield
    finally:
        context.clear()


def is_flag_enabled(flag_identifier: str, default_value, expected_value,
                    fallback_func=None):
    def decorator_check_flag(func):
        @functools.wraps(func)
        def wrapper_check_flag(*args, **kwargs):
            ff_client = context.get('ff_client')
            eval_target = context.get('eval_target')

            if ff_client is None or eval_target is None:
                raise ValueError(
                    "ff_client and eval_target must be set in context")

            flag_type = ff_client.get_flag_type(flag_identifier)

            variation_methods = {
                FeatureFlagType.BOOLEAN: lambda: ff_client.bool_variation(
                    flag_identifier, eval_target, default_value),

                FeatureFlagType.STRING: lambda: ff_client.string_variation(
                    flag_identifier, eval_target, default_value),

                FeatureFlagType.INT_OR_FLOAT: lambda:
                ff_client.int_or_float_variation(
                    flag_identifier, eval_target, default_value),

                FeatureFlagType.JSON: lambda: ff_client.json_variation(
                    flag_identifier, eval_target, default_value),

                FeatureFlagType.FLAG_NOT_FOUND: lambda: default_value
            }

            is_enabled = variation_methods[flag_type]()
            if is_enabled == expected_value:
                return func(*args, **kwargs)
            else:
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                return None  # or some default behavior when the flag is not
                # enabled

        return wrapper_check_flag

    return decorator_check_flag


def my_fallback_function(eval_target: Target):
    print(
        f"Flag is disabled for target with identifier '"
        f"{eval_target.identifier}'")


# This example is using a string flag. But you can use the annotation
# with any flag type and the decorator will use the correct variation method.
# Ensure the expected and default values match the flag
# type you are evaluating.
@is_flag_enabled(flag_identifier="stringflag", default_value="default",
                 expected_value="var12", fallback_func=my_fallback_function)
def my_string_feature_function(eval_target: Target):
    print(
        f"stringflag is enabled for target with identifier '"
        f"{eval_target.identifier}'")


@is_flag_enabled(flag_identifier="boolflag", default_value=False,
                 expected_value=True, fallback_func=my_fallback_function)
def my_bool_feature_function(eval_target: Target):
    print(
        f"boolflag is enabled for target with identifier '"
        f"{eval_target.identifier}'")


def main():
    target = Target(identifier='harness')
    client = CfClient("")
    client.wait_for_initialization()

    with feature_flag_context(client, target):
        my_bool_feature_function(target)
        my_string_feature_function(target)


if __name__ == "__main__":
    main()
