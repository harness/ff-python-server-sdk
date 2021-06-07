from typing import Any, Dict

import httpx

from ...client import Client
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    environment_uuid: str,
    target: str,
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/target/{target}/evaluations".format(
        client.base_url, environmentUUID=environment_uuid, target=target
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
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
    client: Client,
    environment_uuid: str,
    target: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        target=target,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    environment_uuid: str,
    target: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        target=target,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)
