from typing import Any, Dict, Optional

import httpx

from featureflags.api.client import AuthenticatedClient
from featureflags.api.types import Response
from featureflags.evaluations.segment import Segment


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    identifier: str,
    environment_uuid: str,
    **params: Any
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/target-segments/" \
        "{identifier}".format(
            client.base_url,
            identifier=identifier,
            environmentUUID=environment_uuid
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


def _parse_response(*, response: httpx.Response) -> Optional[Segment]:
    if response.status_code == 200:
        response_200 = Segment.from_dict(response.json())

        return response_200
    return None


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

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


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
