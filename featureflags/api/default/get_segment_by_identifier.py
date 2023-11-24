from typing import Any, Dict, Optional

import httpx

from featureflags.api.client import AuthenticatedClient
from featureflags.api.types import Response
from featureflags.config import RETRYABLE_CODES
from featureflags.evaluations.segment import Segment

from tenacity import retry_if_result, wait_exponential, \
    stop_after_attempt, Retrying, retry_all

from featureflags.sdk_logging_codes import warning_fetch_group_by_id_retrying
from featureflags.util import log

MAX_RETRY_ATTEMPTS = 10


def _get_kwargs(
        *,
        client: AuthenticatedClient,
        identifier: str,
        environment_uuid: str,
        **params: Any
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/target-segments/" \
          "{identifier}".format(client.base_url, identifier=identifier,
                                environmentUUID=environment_uuid)

    query_params = {
        **client.get_params(),
        **params
    }

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "params": query_params,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Segment]:
    return Segment.from_dict(response.json())


def _build_response(*, response: httpx.Response) -> Response[Segment]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
        *,
        client: AuthenticatedClient,
        identifier: str,
        environment_uuid: str,
        **params: Any
) -> Response[Segment]:
    kwargs = _get_kwargs(
        client=client,
        identifier=identifier,
        environment_uuid=environment_uuid,
        **params
    )

    retryer = Retrying(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_all(
            retry_if_result(lambda r: r.status_code != 200),
            retry_if_result(handle_http_result)
        ),
        before_sleep=lambda retry_state: warning_fetch_group_by_id_retrying(
            retry_state.attempt_number,
            retry_state.outcome.result()),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    )

    response = retryer(httpx.get, **kwargs)

    return _build_response(response=response)


def handle_http_result(response):
    code = response.status_code
    if code in RETRYABLE_CODES:
        return True
    else:
        # TODO - revisit these error logs, we need to log the SDK code, but
        # do we want to do it here, or by the caller?
        log.error(
            f'Fetching segment by identifier received code #{code} and '
            'will not retry')
        return False


def sync(
        *,
        client: AuthenticatedClient,
        identifier: str,
        environment_uuid: str,
        **params: Any
) -> Optional[Segment]:
    """ """

    return sync_detailed(
        client=client,
        identifier=identifier,
        environment_uuid=environment_uuid,
        **params
    ).parsed


async def asyncio_detailed(
        *,
        client: AuthenticatedClient,
        identifier: str,
        environment_uuid: str,
        **params: Any
) -> Response[Segment]:
    kwargs = _get_kwargs(
        client=client,
        identifier=identifier,
        environment_uuid=environment_uuid,
        **params
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)
