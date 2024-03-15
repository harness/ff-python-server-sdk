from typing import Any, Dict

import httpx

from featureflags.api.client import AuthenticatedClient
from featureflags.api.types import Response
from featureflags.models.metrics import Metrics


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    environment: str,
    json_body: Metrics,
    **params: Any
) -> Dict[str, Any]:
    url = "{}/metrics/{environment}".format(
        client.events_url,
        environment=environment
    )

    query_params = {
        **client.get_params(),
        **params
    }

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    args = {
        "url": url,
        "params": query_params,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }

    if client.tls_trusted_cas_file is not None:
        args["verify"] = client.tls_trusted_cas_file

    return args


def _build_response(*, response: httpx.Response) -> Response[None]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    environment: str,
    json_body: Metrics,
    **params: Any
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        environment=environment,
        json_body=json_body,
        **params
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment: str,
    json_body: Metrics,
    **params: Any
) -> Response[None]:
    kwargs = _get_kwargs(
        client=client,
        environment=environment,
        json_body=json_body,
        **params
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)
