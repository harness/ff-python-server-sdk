import featureflags.sdk_logging_codes as sdk_codes
from featureflags.evaluations.auth_target import Target


def test_logs_dont_raise_exception():
    target = Target(identifier='harness', name="asd")
    sdk_codes.info_poll_started(60)
    sdk_codes.info_sdk_init_ok()
    sdk_codes.info_sdk_init_waiting()
    sdk_codes.info_sdk_start_close()
    sdk_codes.info_sdk_close_success()
    sdk_codes.info_sdk_auth_ok()
    sdk_codes.info_polling_stopped("streaming active")
    sdk_codes.info_stream_connected()
    sdk_codes.info_stream_event_received("")
    sdk_codes.info_stream_stopped()
    sdk_codes.info_metrics_thread_started(10)
    sdk_codes.info_metrics_thread_existed()
    sdk_codes.info_metrics_success()
    sdk_codes.warn_auth_failed_srv_defaults()
    sdk_codes.warn_failed_init_auth_error()
    sdk_codes.warn_auth_failed_exceed_retries()
    sdk_codes.wan_missing_sdk_key()
    sdk_codes.warn_auth_retying(1, "some error")
    sdk_codes.warn_stream_disconnected("example reason")
    sdk_codes.warn_stream_retrying(5)
    sdk_codes.warn_post_metrics_failed("example reason")
    sdk_codes.warn_default_variation_served("identifier", target, "default")
