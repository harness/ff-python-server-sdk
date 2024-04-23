from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.feature_config import FeatureConfig
from ...types import UNSET, Response, Unset


def _get_kwargs(
    environment_uuid: str,
    identifier: str,
    *,
    cluster: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["cluster"] = cluster

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/client/env/{environment_uuid}/feature-configs/{identifier}".format(
            environment_uuid=environment_uuid,
            identifier=identifier,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[FeatureConfig]:
    if response.status_code == HTTPStatus.OK:
        response_200 = FeatureConfig.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[FeatureConfig]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    environment_uuid: str,
    identifier: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Response[FeatureConfig]:
    """Get feature config

    Args:
        environment_uuid (str):
        identifier (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FeatureConfig]
    """

    kwargs = _get_kwargs(
        environment_uuid=environment_uuid,
        identifier=identifier,
        cluster=cluster,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    environment_uuid: str,
    identifier: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Optional[FeatureConfig]:
    """Get feature config

    Args:
        environment_uuid (str):
        identifier (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FeatureConfig
    """

    return sync_detailed(
        environment_uuid=environment_uuid,
        identifier=identifier,
        client=client,
        cluster=cluster,
    ).parsed


async def asyncio_detailed(
    environment_uuid: str,
    identifier: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Response[FeatureConfig]:
    """Get feature config

    Args:
        environment_uuid (str):
        identifier (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FeatureConfig]
    """

    kwargs = _get_kwargs(
        environment_uuid=environment_uuid,
        identifier=identifier,
        cluster=cluster,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    environment_uuid: str,
    identifier: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Optional[FeatureConfig]:
    """Get feature config

    Args:
        environment_uuid (str):
        identifier (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FeatureConfig
    """

    return (
        await asyncio_detailed(
            environment_uuid=environment_uuid,
            identifier=identifier,
            client=client,
            cluster=cluster,
        )
    ).parsed
