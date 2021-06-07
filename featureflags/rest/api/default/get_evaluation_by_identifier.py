from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.evaluation import Evaluation
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    environment_uuid: str,
    feature: str,
    target: str,
) -> Dict[str, Any]:
    url = (
        "{}/client/env/{environmentUUID}/target/{target}/evaluations/{feature}".format(
            client.base_url,
            environmentUUID=environment_uuid,
            feature=feature,
            target=target,
        )
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Evaluation]:
    if response.status_code == 200:
        response_200 = Evaluation.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[Evaluation]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    environment_uuid: str,
    feature: str,
    target: str,
) -> Response[Evaluation]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        feature=feature,
        target=target,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    environment_uuid: str,
    feature: str,
    target: str,
) -> Optional[Evaluation]:
    """  """

    return sync_detailed(
        client=client,
        environment_uuid=environment_uuid,
        feature=feature,
        target=target,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    environment_uuid: str,
    feature: str,
    target: str,
) -> Response[Evaluation]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        feature=feature,
        target=target,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    environment_uuid: str,
    feature: str,
    target: str,
) -> Optional[Evaluation]:
    """  """

    return (
        await asyncio_detailed(
            client=client,
            environment_uuid=environment_uuid,
            feature=feature,
            target=target,
        )
    ).parsed
