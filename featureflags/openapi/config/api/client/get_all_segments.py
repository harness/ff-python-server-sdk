from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.segment import Segment
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
        "url": "/client/env/{environment_uuid}/target-segments".format(
            environment_uuid=environment_uuid,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, List["Segment"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Segment.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, List["Segment"]]]:
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
) -> Response[Union[Any, List["Segment"]]]:
    """Retrieve all segments.

     Used to retrieve all segments for certain account id.

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['Segment']]]
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
) -> Optional[Union[Any, List["Segment"]]]:
    """Retrieve all segments.

     Used to retrieve all segments for certain account id.

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['Segment']]
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
) -> Response[Union[Any, List["Segment"]]]:
    """Retrieve all segments.

     Used to retrieve all segments for certain account id.

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['Segment']]]
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
) -> Optional[Union[Any, List["Segment"]]]:
    """Retrieve all segments.

     Used to retrieve all segments for certain account id.

    Args:
        environment_uuid (str):
        cluster (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['Segment']]
    """

    return (
        await asyncio_detailed(
            environment_uuid=environment_uuid,
            client=client,
            cluster=cluster,
        )
    ).parsed
