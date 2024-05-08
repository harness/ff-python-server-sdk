from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_number: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    cluster: Union[Unset, str] = UNSET,
    environment: Union[Unset, str] = UNSET,
    key: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["pageNumber"] = page_number

    params["pageSize"] = page_size

    params["cluster"] = cluster

    params["environment"] = environment

    params["key"] = key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/proxy/config",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return None
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        return None
    if response.status_code == HTTPStatus.FORBIDDEN:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    cluster: Union[Unset, str] = UNSET,
    environment: Union[Unset, str] = UNSET,
    key: str,
) -> Response[Any]:
    """Gets Proxy config for multiple environments

     Gets Proxy config for multiple environments if the Key query param is provided or gets config for a
    single environment if an environment query param is provided

    Args:
        page_number (Union[Unset, int]):
        page_size (Union[Unset, int]):
        cluster (Union[Unset, str]):
        environment (Union[Unset, str]):
        key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        page_number=page_number,
        page_size=page_size,
        cluster=cluster,
        environment=environment,
        key=key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page_number: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    cluster: Union[Unset, str] = UNSET,
    environment: Union[Unset, str] = UNSET,
    key: str,
) -> Response[Any]:
    """Gets Proxy config for multiple environments

     Gets Proxy config for multiple environments if the Key query param is provided or gets config for a
    single environment if an environment query param is provided

    Args:
        page_number (Union[Unset, int]):
        page_size (Union[Unset, int]):
        cluster (Union[Unset, str]):
        environment (Union[Unset, str]):
        key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        page_number=page_number,
        page_size=page_size,
        cluster=cluster,
        environment=environment,
        key=key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
