"""Tests for FFM-13056: SDK must recover after a failed initialization.

Bug: if the initial flags/segments fetch failed, the SDK latched
`initialised_failed_reason[True]` forever. The background polling loop
kept fetching successfully, but the latch was never cleared, so every
variation kept returning defaults until the pod/client was restarted.

Fix: a successful poll after a failed init clears the latch, so
`CfClient.is_initialized()` flips back to True and evaluations resume
serving real values.
"""

import time
from threading import Event
from unittest.mock import MagicMock, patch

from featureflags.api import UnrecoverableRequestException
from featureflags.config import default_config
from featureflags.polling import PollingProcessor


def _make_processor(failed_reason):
    config = default_config
    config.enable_stream = True  # skip the pre-loop pull_interval sleep
    return PollingProcessor(
        client=MagicMock(),
        config=config,
        environment_id="test-env",
        wait_for_initialization=Event(),
        initialised_failed_reason=failed_reason,
        ready=Event(),
        stream_ready=Event(),
        repository=MagicMock(),
        cluster="1",
    )


def _ok_response():
    response = MagicMock()
    response.parsed = []
    return response


def _wait_for(predicate, timeout=5):
    deadline = time.time() + timeout
    while not predicate() and time.time() < deadline:
        time.sleep(0.05)
    return predicate()


def test_latch_cleared_when_poll_succeeds_after_failed_init():
    failed_reason = {False: None, True: None}
    processor = _make_processor(failed_reason)

    call_count = {"flags": 0}
    allow_success = Event()

    def fail_once_then_succeed(*args, **kwargs):
        call_count["flags"] += 1
        if call_count["flags"] == 1:
            raise UnrecoverableRequestException(500, "server error")
        # hold the recovery fetch until the test has observed the latch
        allow_success.wait(timeout=5)
        return _ok_response()

    with patch("featureflags.polling.retryable_retrieve_feature_config",
               side_effect=fail_once_then_succeed), \
         patch("featureflags.polling.retryable_retrieve_segments",
               return_value=_ok_response()):
        processor.start()
        try:
            assert _wait_for(lambda: failed_reason[True] is not None), \
                "expected init failure to latch the failed reason"
            allow_success.set()
            assert _wait_for(lambda: failed_reason[True] is None), \
                "expected successful poll to clear the latched failure"
            assert call_count["flags"] >= 2
        finally:
            allow_success.set()
            processor.stop()


def test_latch_stays_set_while_polls_keep_failing():
    failed_reason = {False: None, True: None}
    processor = _make_processor(failed_reason)

    def always_fail(*args, **kwargs):
        raise UnrecoverableRequestException(500, "server error")

    with patch("featureflags.polling.retryable_retrieve_feature_config",
               side_effect=always_fail), \
         patch("featureflags.polling.retryable_retrieve_segments",
               side_effect=always_fail):
        processor.start()
        try:
            assert _wait_for(lambda: failed_reason[True] is not None)
            time.sleep(1)  # a failing poll cycle must not clear it
            assert failed_reason[True] is not None
        finally:
            processor.stop()
