import threading
import types
from unittest import mock

from featureflags import polling, streaming
from featureflags.config import Config
from featureflags.polling import PollingProcessor
from featureflags.streaming import StreamProcessor


class FakeRepository(object):
    def __init__(self):
        self.flags = {}

    def set_flag(self, flag):
        self.flags[flag.feature] = flag

    def set_segment(self, segment):
        pass


def test_update_sent_while_stream_reconnects_is_fetched(monkeypatch):
    """The proxy closes the stream and a flag changes before the SDK
    reconnects. The SDK must poll after reconnecting to pick up the change."""
    flag_version = {"value": 1}
    polled_versions = []
    poll_done = threading.Condition()

    def retrieve_flags(**kwargs):
        version = flag_version["value"]
        with poll_done:
            polled_versions.append(version)
            poll_done.notify_all()
        return mock.Mock(parsed=[mock.Mock(feature="flag", version=version)])

    monkeypatch.setattr(polling, "retryable_retrieve_feature_config",
                        retrieve_flags)
    monkeypatch.setattr(polling, "retryable_retrieve_segments",
                        lambda **kwargs: mock.Mock(parsed=[]))

    close_first_stream = threading.Event()
    release_backoff = threading.Event()
    stop = threading.Event()

    def first_stream():
        close_first_stream.wait()
        raise EOFError("Stream closed by server")
        yield

    def second_stream():
        stop.wait()
        return
        yield

    streams = iter([first_stream(), second_stream()])
    monkeypatch.setattr(StreamProcessor, "_connect",
                        lambda self: next(streams))
    monkeypatch.setattr(streaming, "time", types.SimpleNamespace(
        sleep=lambda seconds: release_backoff.wait()))

    def wait_for_polls(count):
        with poll_done:
            return poll_done.wait_for(lambda: len(polled_versions) >= count,
                                      timeout=5)

    config = Config(enable_stream=True)
    repository = FakeRepository()
    stream_ready = threading.Event()
    poll_requested = threading.Event()
    poller = PollingProcessor(
        client=mock.Mock(), config=config, environment_id="env",
        wait_for_initialization=threading.Event(),
        initialised_failed_reason={False: ""}, ready=poll_requested,
        stream_ready=stream_ready, repository=repository, cluster="1")
    stream = StreamProcessor(
        repository=repository, client=mock.Mock(), environment_id="env",
        api_key="key", token="token", config=config, ready=stream_ready,
        poller=poll_requested, cluster="1")

    poller.start()
    stream.start()
    try:
        # Initial fetch, plus the poll requested when the stream connects
        assert wait_for_polls(2)

        # The proxy closes the stream; the SDK polls on disconnect
        polls_before_disconnect = len(polled_versions)
        close_first_stream.set()
        assert wait_for_polls(polls_before_disconnect + 1)

        # The flag changes while the SDK is waiting to reconnect, so the
        # stream event for it is never received
        flag_version["value"] = 2
        release_backoff.set()

        with poll_done:
            assert poll_done.wait_for(lambda: 2 in polled_versions,
                                      timeout=5)
        assert repository.flags["flag"].version == 2
    finally:
        stream.stop()
        poller.stop()
        stop.set()
        release_backoff.set()
