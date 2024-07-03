import pytest
import time

from featureflags.client import CfClient, SDKInitTimeoutException
from featureflags.config import *

def test_wait_timeout(mocker):
    def mock_run():
        time.sleep(.5)
    mocker.patch("featureflags.client.CfClient.run",
                     side_effect=mock_run)
    client = CfClient("test")
    exception_caught = False
    # timeout will trigger since ckient._initialized event will never set.
    try:
        client.wait_for_initialization(timeout_delay=1)
    except SDKInitTimeoutException:
        exception_caught = True

    assert exception_caught
