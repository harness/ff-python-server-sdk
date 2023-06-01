from typing import Any, Dict, Optional, Union

import httpx

from featureflags.api.client import Client
from featureflags.api.types import Response
from featureflags.models.authentication_request import AuthenticationRequest
from featureflags.models.authentication_response import AuthenticationResponse
from tenacity import retry, retry_if_result, wait_exponential


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


def _parse_response(
        *, response: httpx.Response
) -> Optional[Union[AuthenticationResponse, None]]:
    if response.status_code == 200:
        response_200 = AuthenticationResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = None

        return response_401
    if response.status_code == 403:
        response_403 = None

        return response_403
    if response.status_code == 404:
        response_404 = None

        return response_404
    if response.status_code == 500:
        response_500 = None

        return response_500
    return None


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

    response = _post_request(kwargs)

    return _build_response(response=response)


def handle_http_result(response):
    # 408 request timeout
    # 425 too early
    # 429 too many requests
    # 500 internal server error
    # 502 bad gateway
    # 503 service unavailable
    # 504 gateway timeout
    #  -1 OpenAPI error (timeout etc.)
    if response.status_code in [408, 425, 429, 500, 502, 503, 504, -1]:
        return True
    else:
        return False


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=(
        retry_if_result(lambda response: response.status_code != 200) and
        retry_if_result(handle_http_result))
)
def _post_request(kwargs):
    return httpx.post(
        **kwargs,
    )


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
