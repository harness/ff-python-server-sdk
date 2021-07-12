from typing import Any, Dict, Optional

import httpx

from ...evaluations.feature import FeatureConfig
from ..client import AuthenticatedClient
from ..types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    identifier: str,
    environment_uuid: str,
    **params: Any
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/feature-configs/" \
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


def _parse_response(*, response: httpx.Response) -> Optional[FeatureConfig]:
    if response.status_code == 200:
        response_200 = FeatureConfig.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[FeatureConfig]:
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
) -> Response[FeatureConfig]:
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
) -> Optional[FeatureConfig]:
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
) -> Response[FeatureConfig]:
    kwargs = _get_kwargs(
        client=client,
        identifier=identifier,
        environment_uuid=environment_uuid,
        **params
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    identifier: str,
    environment_uuid: str,
    **params
) -> Optional[FeatureConfig]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            identifier=identifier,
            environment_uuid=environment_uuid,
            **params
        )
    ).parsed
