from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    environment_id: str,
) -> Dict[str, Any]:
    url = "{}/stream/environments/{environmentId}".format(
        client.base_url, environmentId=environment_id
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[None, None]]:
    if response.status_code == 200:
        response_200 = None

        return response_200
    if response.status_code == 503:
        response_503 = None

        return response_503
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[None, None]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    environment_id: str,
) -> Response[Union[None, None]]:
    kwargs = _get_kwargs(
        client=client,
        environment_id=environment_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    environment_id: str,
) -> Optional[Union[None, None]]:
    """  """

    return sync_detailed(
        client=client,
        environment_id=environment_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_id: str,
) -> Response[Union[None, None]]:
    kwargs = _get_kwargs(
        client=client,
        environment_id=environment_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    environment_id: str,
) -> Optional[Union[None, None]]:
    """  """

    return (
        await asyncio_detailed(
            client=client,
            environment_id=environment_id,
        )
    ).parsed
