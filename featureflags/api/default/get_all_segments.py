from typing import Any, Dict, List, Optional

import httpx

from featureflags.api.client import AuthenticatedClient
from featureflags.api.types import Response
from featureflags.evaluations.segment import Segment


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/target-segments".format(
        client.base_url, environmentUUID=environment_uuid
    )

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


def _parse_response(*, response: httpx.Response) -> Optional[List[Segment]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Segment.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[Segment]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Response[List[Segment]]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        **params
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any,
) -> Optional[List[Segment]]:
    """All segment groups in project environment"""

    return sync_detailed(
        client=client,
        environment_uuid=environment_uuid,
        **params
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Response[List[Segment]]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        **params
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Optional[List[Segment]]:
    """All segment groups"""

    return (
        await asyncio_detailed(
            client=client,
            environment_uuid=environment_uuid,
            **params
        )
    ).parsed
