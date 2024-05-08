from featureflags.util import log


def get_sdk_code_message(key):
    sdk_codes = {
        # SDK_INIT_1xxx
        1000: "The SDK has successfully initialized",
        1001: "The SDK has failed to initialize due to an authentication "
              "error and defaults will be served, reason:",
        1002: "The SDK has failed to initialize due to a missing or empty "
              "API key and defaults will be served",
        1003: "The SDK is waiting for initialization to complete",
        1006: "The SDK has failed to initialize and defaults will be served, "
              "reason:",
        # SDK_AUTH_2xxx
        2000: "Authentication was successful",
        2001: "Authentication failed with a non-recoverable error",
        2002: "Authentication attempt",
        2003: "Authentication failed and max retries have been exceeded",
        # SDK_CLOSE_3xxx
        3000: "Closing SDK",
        3001: "SDK Closed successfully",
        # SDK_POLL_4xxx
        4000: "Polling started, intervalMs:",
        4001: "Polling stopped, reason:",
        4002: "Polled flags and groups successfully",
        # SDK_STREAM_5xxx
        5000: "SSE stream successfully connected",
        5001: "SSE stream disconnected, reason:",
        5002: "SSE event received: ",
        5003: "SSE retrying to connect in",
        5004: "SSE stopped",
        5005: "Stream is still retrying after 5 retries",
        # SDK_EVAL_6xxx - these are hardcoded in `variation.py` as they
        # are more complex
        # SDK_METRICS_7xxx
        7000: "Metrics thread started with request interval:",
        7001: "Metrics thread exited",
        7002: "Posting metrics failed, reason:",
        7003: "Metrics posted successfully",
        7004: "Target metrics exceeded max size, remaining targets for this "
              "analytics interval will not be sent",
        7005: "Target metrics batches succeeded:",
        7006: "Target metrics batch/batches failed:",
        7007: "Evaluation metrics exceeded max size, remaining unique "
              "evaluations for this analytics interval will not be sent",
        # SDK_CACHE_8xxx
        8005: "Fetching feature by identifier attempt",
        8006: "Fetching segment by identifier attempt",
        8007: "Fetching all features attempt",
        8008: "Fetching all segments attempt",
        8009: "Fetching feature by identifier failed, reason: ",
        8010: "Fetching segment by identifier failed, reason: ",
        8011: "Fetching all features failed, reason: ",
        8012: "Fetching all segments failed, reason: ",
    }
    if key in sdk_codes:
        return sdk_codes[key]
    else:
        return "Unknown SDK code"


def sdk_err_msg(error_code, append_text=""):
    return f"SDKCODE:{error_code}: {get_sdk_code_message(error_code)} " \
           f"{append_text} "


def wan_missing_sdk_key():
    msg = sdk_err_msg(1002)
    log.warning(msg)


def info_poll_started(duration_sec):
    log.info(sdk_err_msg(4000, duration_sec * 1000))


def info_poll_ran_successfully():
    log.info(sdk_err_msg(4002))


def info_sdk_init_ok():
    log.info(sdk_err_msg(1000))


def info_sdk_init_waiting():
    log.info(sdk_err_msg(1003))


def info_sdk_start_close():
    log.info(sdk_err_msg(3000))


def info_sdk_close_success():
    log.info(sdk_err_msg(3001))


def info_sdk_auth_ok():
    log.info(sdk_err_msg(2000))


def info_polling_stopped(reason):
    log.info(sdk_err_msg(4001, reason))


def info_stream_connected():
    log.info(sdk_err_msg(5000))


def info_stream_event_received(event_json):
    log.info(sdk_err_msg(5002, event_json))


def info_stream_stopped():
    log.info(sdk_err_msg(5004))


def info_metrics_thread_started(interval):
    log.info(sdk_err_msg(7000, interval))


def info_metrics_success():
    log.info(sdk_err_msg(7003))


def info_metrics_target_exceeded():
    log.info(sdk_err_msg(7004))


def info_metrics_target_batch_success(message):
    log.info(sdk_err_msg(7005, message))


def info_evaluation_metrics_exceeded():
    log.info(sdk_err_msg(7007))


def info_metrics_thread_existed():
    log.info(sdk_err_msg(7001))


def info_eval_success():
    log.info(sdk_err_msg(6000))


def warn_auth_failed_srv_defaults():
    log.warning(sdk_err_msg(2001))


def warn_failed_init_auth_error(error=""):
    log.warning(sdk_err_msg(1001, error))


def warn_failed_init_fetch_error(error=""):
    log.warning(sdk_err_msg(1006, error))


def warn_auth_failed_exceed_retries():
    log.warning(sdk_err_msg(2003))


def warn_auth_retying(attempt, error):
    log.warning(sdk_err_msg(2002,
                            f"{attempt}, got error: '{error}', "
                            f"Retrying ..."))


def warn_stream_disconnected(reason):
    log.warning(sdk_err_msg(5001, reason))


def warn_stream_retrying(seconds):
    log.warning(sdk_err_msg(5003, seconds))


def warn_stream_retrying_long_duration():
    log.warning(sdk_err_msg(5005))


def warn_post_metrics_failed(reason):
    log.warning(sdk_err_msg(7002, reason))


def warn_post_metrics_target_batch_failed(message):
    log.warning(sdk_err_msg(7006, message))


def warning_fetch_feature_by_id_retrying(attempt, error):
    log.warning(sdk_err_msg(8005,
                            f"{attempt}, got error: '{error}', "
                            f"Retrying ..."))


def warning_fetch_group_by_id_retrying(attempt, error):
    log.warning(sdk_err_msg(8006,
                            f"{attempt}, got error: '{error}', "
                            f"Retrying ..."))


def warning_fetch_all_features_retrying(attempt, error):
    log.warning(sdk_err_msg(8007,
                            f"{attempt}, got error: '{error}', "
                            f"Retrying ..."))


def warning_fetch_all_segments_retrying(attempt, error):
    log.warning(sdk_err_msg(8008,
                            f"{attempt}, got error: '{error}', "
                            f"Retrying ..."))


def warning_fetch_feature_by_id_failed(error):
    log.warning(sdk_err_msg(8009,
                            f"{error}"))


def warning_fetch_group_by_id_failed(error):
    log.warning(sdk_err_msg(8010,
                            f"{error}"))


def warning_fetch_all_features_failed(error):
    log.warning(sdk_err_msg(8011,
                            f"{error}"))


def warning_fetch_all_groups_failed(error):
    log.warning(sdk_err_msg(8012,
                            f"{error}"))
