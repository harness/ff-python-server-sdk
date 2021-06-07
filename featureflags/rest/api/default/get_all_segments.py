from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.segment import Segment
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/target-segments".format(
        client.base_url, environmentUUID=environment_uuid
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[List[Segment], None, None, None, None]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Segment.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[List[Segment], None, None, None, None]]:
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
) -> Response[Union[List[Segment], None, None, None, None]]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
) -> Optional[Union[List[Segment], None, None, None, None]]:
    """ Used to retrieve all segments for certain account id. """

    return sync_detailed(
        client=client,
        environment_uuid=environment_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
) -> Response[Union[List[Segment], None, None, None, None]]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
) -> Optional[Union[List[Segment], None, None, None, None]]:
    """ Used to retrieve all segments for certain account id. """

    return (
        await asyncio_detailed(
            client=client,
            environment_uuid=environment_uuid,
        )
    ).parsed
