from typing import Any, Dict, Optional, Union
from featureflags.util import log

import httpx

from featureflags.api.client import Client
from featureflags.api.types import Response
from featureflags.models.authentication_request import AuthenticationRequest
from featureflags.models.authentication_response import AuthenticationResponse
from tenacity import retry, retry_if_result, wait_exponential, \
    stop_after_attempt, Retrying


def _get_kwargs(
        *,
        client: Client,
        json_body: AuthenticationRequest,
) -> Dict[str, Any]:
    url = "{}/client/auth".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


# TODO fix response for else condition
def _parse_response(
        *, response: httpx.Response
) -> Optional[Union[AuthenticationResponse, None]]:
    if response.status_code == 200:
        response_200 = AuthenticationResponse.from_dict(response.json())
    else:
        raise Exception('Authentication failed on an unrecoverable error')


def _build_response(
        *, response: httpx.Response
) -> Response[Union[AuthenticationResponse, None]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
        *,
        client: Client,
        json_body: AuthenticationRequest,
) -> Response[Union[AuthenticationResponse, None]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    max_auth_retries = client.get_max_auth_retries()
    response = _post_request(kwargs, max_auth_retries)

    return _build_response(response=response)


def handle_http_result(response):
    # 408 request timeout
    # 425 too early
    # 429 too many requests
    # 500 internal server error
    # 502 bad gateway
    # 503 service unavailable
    # 504 gateway timeout
    code = response.status_code
    if code in [409, 425, 429, 500, 502, 503, 504]:
        return True
    else:
        log.error(f'Authentication failed with HTTP code #{code} and '
                  'will not attempt to reconnect')
        return False


def _post_request(kwargs, max_auth_retries):
    retryer = Retrying(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=(
                retry_if_result(
                    lambda response: response.status_code != 200) and
                retry_if_result(handle_http_result)),
        before_sleep=lambda retry_state: log.warning(
            f'Authentication attempt #{retry_state.attempt_number} '
            f'got {retry_state.outcome.result()} Retrying...'),
        stop=stop_after_attempt(max_auth_retries),
    )
    return retryer(httpx.post, **kwargs)


def sync(
        *,
        client: Client,
        json_body: AuthenticationRequest,
) -> Optional[Union[AuthenticationResponse, None]]:
    """Used to retrieve all target segments for certain account id."""

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
        *,
        client: Client,
        json_body: AuthenticationRequest,
) -> Response[Union[AuthenticationResponse, None]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
        *,
        client: Client,
        json_body: AuthenticationRequest,
) -> Optional[Union[AuthenticationResponse, None]]:
    """Used to retrieve all target segments for certain account id."""

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
