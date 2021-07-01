"""
Server Sent Event (SSE) client

Based on: https://github.com/btubbs/sseclient
"""

import codecs
import re
import time
import warnings
from typing import Any, Dict, Generator, List, Match, Optional, Pattern

import requests
from requests.models import Response

from .util import log

# Technically, we should support streams that mix line endings.  This regex,
# however, assumes that a system will provide consistent line endings.
end_of_field: Pattern[str] = re.compile(r"\r\n\r\n|\r\r|\n\n")


class SSEClient(object):
    def __init__(
        self,
        url: str,
        last_id: str = None,
        retry: int = 3000,
        session: Any = None,
        chunk_size: int = 1024,
        **kwargs: Dict[str, Any]
    ):
        self.url = url
        self.last_id = last_id
        self.retry = retry
        self.chunk_size = chunk_size

        # Optional support for passing in a requests.Session()
        self.session = session

        # Any extra kwargs will be fed into the requests.get call later.
        self.requests_kwargs = kwargs

        # The SSE spec requires making requests with Cache-Control: nocache
        if "headers" not in self.requests_kwargs:
            self.requests_kwargs["headers"] = {}
        self.requests_kwargs["headers"]["Cache-Control"] = "no-cache"

        # The 'Accept' header is not required, but explicit > implicit
        self.requests_kwargs["headers"]["Accept"] = "text/event-stream"

        # Keep data here as it streams in
        self.buf: str = ""

        self._connect()

    def _connect(self):
        if self.last_id:
            self.requests_kwargs["headers"]["Last-Event-ID"] = self.last_id

        # Use session if set.  Otherwise fall back to requests module.
        requester = self.session or requests
        self.resp: Response = requester.get(
            self.url, stream=True, **self.requests_kwargs
        )
        self.resp_iterator: Generator[Any, None, None] = self.iter_content()
        encoding: str = self.resp.encoding or self.resp.apparent_encoding
        self.decoder = codecs.getincrementaldecoder(encoding)(errors="replace")

        # TODO: Ensure we're handling redirects.  Might also stick the 'origin'
        # attribute on Events like the Javascript spec requires.
        self.resp.raise_for_status()

    def iter_content(self):
        def generate():
            while True:
                if (
                    hasattr(self.resp.raw, "_fp")
                    and hasattr(self.resp.raw._fp, "fp")
                    and hasattr(self.resp.raw._fp.fp, "read1")
                ):
                    chunk = self.resp.raw._fp.fp.read1(self.chunk_size)
                else:
                    # _fp is not available, this means that we cannot use short
                    # reads and this will block until the full chunk size is
                    # actually read
                    chunk = self.resp.raw.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

        return generate()

    def _event_complete(self):
        return re.search(end_of_field, self.buf) is not None

    def __iter__(self):
        return self

    def __next__(self):
        while not self._event_complete():
            try:
                next_chunk = next(self.resp_iterator)
                if not next_chunk:
                    raise EOFError()
                self.buf += self.decoder.decode(next_chunk)

            except (StopIteration, requests.RequestException, EOFError) as e:
                log.error(e)
                time.sleep(self.retry / 1000.0)
                self._connect()

                # The SSE spec only supports resuming from a whole message, so
                # if we have half a message we should throw it out.
                head, sep, _ = self.buf.rpartition("\n")
                self.buf = head + sep
                continue

        # Split the complete event (up to the end_of_field) into event_string,
        # and retain anything after the current complete event in self.buf
        # for next time.
        event: str
        (event, self.buf) = re.split(end_of_field, self.buf, maxsplit=1)
        msg: Event = Event.parse(event)

        # If the server requests a specific retry delay, we need to honor it.
        if msg.retry:
            self.retry = msg.retry

        # last_id should only be set if included in the message.  It's not
        # forgotten if a message omits it.
        if msg.id:
            self.last_id = msg.id

        return msg


class Event(object):

    sse_line_pattern: Pattern[str] = re.compile(
        "(?P<name>[^:]*):?( ?(?P<value>.*))?"
    )

    def __init__(
        self,
        data: str = "",
        event: str = "message",
        id: Optional[str] = None,
        retry: Optional[int] = None,
    ):
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry

    def dump(self):
        lines: List[str] = []
        if self.id:
            lines.append("id: %s" % self.id)

        # Only include an event line if it's not the default already.
        if self.event != "message":
            lines.append("event: %s" % self.event)

        if self.retry:
            lines.append("retry: %s" % self.retry)

        lines.extend("data: %s" % d for d in self.data.split("\n"))
        return "\n".join(lines) + "\n\n"

    @classmethod
    def parse(cls, raw: str) -> "Event":
        """
        Given a possibly-multiline string representing an SSE message, parse it
        and return a Event object.
        """
        msg: Event = cls()
        for line in raw.splitlines():
            m: Optional[Match[str]] = cls.sse_line_pattern.match(line)
            if m is None:
                # Malformed line.  Discard but warn.
                warnings.warn('Invalid SSE line: "%s"' % line, SyntaxWarning)
                continue

            name: str = m.group("name")
            if name == "":
                # line began with a ":", so is a comment.  Ignore
                continue
            value: str = m.group("value")

            if name == "data":
                # If we already have some data, then join to it with a newline.
                # Else this is it.
                if msg.data:
                    msg.data = "%s\n%s" % (msg.data, value)
                else:
                    msg.data = value
            elif name == "event":
                msg.event = value
            elif name == "id":
                msg.id = value
            elif name == "retry":
                msg.retry = int(value)

        return msg

    def __str__(self) -> str:
        return self.data
