from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.feature_config import FeatureConfig
from ...types import UNSET, Response, Unset


def _get_kwargs(
    environment_uuid: str,
    *,
    cluster: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["cluster"] = cluster

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/client/env/{environment_uuid}/feature-configs".format(
            environment_uuid=environment_uuid,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["FeatureConfig"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = FeatureConfig.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["FeatureConfig"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    environment_uuid: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Response[List["FeatureConfig"]]:
    """Get all feature flags activations

     All feature flags with activations in project environment

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['FeatureConfig']]
    """

    kwargs = _get_kwargs(
        environment_uuid=environment_uuid,
        cluster=cluster,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    environment_uuid: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Optional[List["FeatureConfig"]]:
    """Get all feature flags activations

     All feature flags with activations in project environment

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['FeatureConfig']
    """

    return sync_detailed(
        environment_uuid=environment_uuid,
        client=client,
        cluster=cluster,
    ).parsed


async def asyncio_detailed(
    environment_uuid: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Response[List["FeatureConfig"]]:
    """Get all feature flags activations

     All feature flags with activations in project environment

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['FeatureConfig']]
    """

    kwargs = _get_kwargs(
        environment_uuid=environment_uuid,
        cluster=cluster,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    environment_uuid: str,
    *,
    client: AuthenticatedClient,
    cluster: Union[Unset, str] = UNSET,
) -> Optional[List["FeatureConfig"]]:
    """Get all feature flags activations

     All feature flags with activations in project environment

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['FeatureConfig']
    """

    return (
        await asyncio_detailed(
            environment_uuid=environment_uuid,
            client=client,
            cluster=cluster,
        )
    ).parsed
