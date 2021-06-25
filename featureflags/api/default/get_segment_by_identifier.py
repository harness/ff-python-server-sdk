from typing import Any, Dict

import httpx

from ...client import AuthenticatedClient
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    identifier: str,
    environment_uuid: str,
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/target-segments/{identifier}".format(
        client.base_url, identifier=identifier, environmentUUID=environment_uuid
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
    client: AuthenticatedClient,
    identifier: str,
    environment_uuid: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        identifier=identifier,
        environment_uuid=environment_uuid,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    identifier: str,
    environment_uuid: str,
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        identifier=identifier,
        environment_uuid=environment_uuid,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)
