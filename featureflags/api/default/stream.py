from typing import Any, Dict

import httpx

from ..client import AuthenticatedClient
from ..types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    api_key: str,
    **params: Any
) -> Dict[str, Any]:
    url = "{}/stream".format(client.base_url)

    query_params = {
        **client.get_params(),
        **params
    }

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    headers["api-key"] = api_key

    return {
        "url": url,
        "params": query_params,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _build_response(*, response: httpx.Response) -> Response[None]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    api_key: str,
    **params: Any
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        api_key=api_key,
        **params
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    api_key: str,
    **params: Any
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        api_key=api_key,
        **params
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)
