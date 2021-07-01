from typing import Any, Dict, List, Optional

import httpx

from featureflags.evaluations.feature import FeatureConfig

from ..client import AuthenticatedClient
from ..types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/feature-configs".format(
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
    *,
    response: httpx.Response
) -> Optional[List[FeatureConfig]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = FeatureConfig.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    return None


def _build_response(
    *,
    response: httpx.Response
) -> Response[List[FeatureConfig]]:
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
) -> Response[List[FeatureConfig]]:
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
) -> Optional[List[FeatureConfig]]:
    """All feature flags with activations in project environment"""

    return sync_detailed(
        client=client,
        environment_uuid=environment_uuid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
) -> Response[List[FeatureConfig]]:
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
) -> Optional[List[FeatureConfig]]:
    """All feature flags with activations in project environment"""

    return (
        await asyncio_detailed(
            client=client,
            environment_uuid=environment_uuid,
        )
    ).parsed
