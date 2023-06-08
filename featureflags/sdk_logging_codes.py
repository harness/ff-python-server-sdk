from featureflags.util import log


def get_sdk_code_message(key):
    sdk_codes = {
        # SDK_INIT_1xxx
        1000: "The SDK has successfully initialized",
        1001: "The SDK has failed to initialize due to the following "
              "authentication error:",
        1002: "The SDK has failed to initialize due to a missing or empty "
              "API key",
        1003: "The SDK is waiting for initialization to complete",
        # SDK_AUTH_2xxx
        2000: "Authenticated ok",
        2001: "Authentication failed with a non-recoverable error - defaults "
              "will be served",
        2002: "Authentication attempt",
        2003: "Authentication failed and max retries have been exceeded - "
              "defaults will be servied",
        # SDK_POLL_4xxx
        4000: "Polling started, intervalMs:",
        4001: "Polling stopped, reason:",
        # SDK_STREAM_5xxx
        5000: "SSE stream connected ok",
        5001: "SSE stream disconnected, reason:",
        5002: "SSE event received: ",
        5003: "SSE retrying to connect in",
        # SDK_EVAL_6xxx
        6000: "Evaluated variation successfully",
        6001: "Default variation was served",
        # SDK_METRICS_7xxx
        7000: "Metrics thread started with request interval:",
        7001: "Metrics thread exited",
        7002: "Posting metrics failed, reason:",
        7003: "Metrics posted successfully",
    }
    if key in sdk_codes:
        return sdk_codes[key]
    else:
        return "Unknown SDK code"


def sdk_err_msg(error_code, append_text=""):
    return f"SDKCODE:{error_code}: {get_sdk_code_message(error_code)} " \
           f"{append_text} "


def raise_missing_sdk_key():
    msg = sdk_err_msg(1002)
    log.error(msg)
    raise Exception(msg)


def info_poll_started(duration_sec):
    log.info(sdk_err_msg(4000, duration_sec * 1000))


def info_sdk_init_ok():
    log.info(sdk_err_msg(1000))


def info_sdk_init_waiting():
    log.info(sdk_err_msg(1003))


def info_sdk_auth_ok():
    log.info(sdk_err_msg(2000))


def info_polling_stopped(reason):
    log.info(sdk_err_msg(4001, reason))


def info_stream_connected():
    log.info(sdk_err_msg(5000))


def info_stream_event_received(event_json):
    log.info(sdk_err_msg(5002, event_json))


def info_metrics_thread_started(interval):
    log.info(sdk_err_msg(7000, interval))


def info_metrics_success():
    log.info(sdk_err_msg(7003))


def warn_auth_failed_srv_defaults():
    log.warning(sdk_err_msg(2001))


def warn_auth_failed_exceed_retries():
    log.warning(sdk_err_msg(2003))


def warn_auth_retying(attempt, error):
    log.warning(sdk_err_msg(2002,
                            f"attempt {attempt}, got error: {error}, "
                            f"Retrying ..."))


def warn_stream_disconnected(reason):
    log.warning(sdk_err_msg(5001, reason))


def warn_stream_retrying(seconds):
    log.warning(sdk_err_msg(5003, seconds))


def warn_post_metrics_failed(reason):
    log.warning(sdk_err_msg(7002, reason))


def warn_default_variation_served(flag, target, default):
    log.warning(sdk_err_msg(6001,
                            f"flag={flag}, "
                            f"target={target}, default={default}"))
