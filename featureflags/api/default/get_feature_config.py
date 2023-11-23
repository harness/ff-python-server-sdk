from typing import Any, Dict, List, Optional

import httpx

from featureflags.api.client import AuthenticatedClient
from featureflags.api.types import Response
from featureflags.config import RETRYABLE_CODES
from featureflags.evaluations.feature import FeatureConfig

from tenacity import retry_if_result, wait_exponential, \
    stop_after_attempt, Retrying, retry_all

from featureflags.sdk_logging_codes import warning_fetch_all_features_retrying
from featureflags.util import log

MAX_RETRY_ATTEMPTS = 2



def _get_kwargs(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Dict[str, Any]:
    url = "{}/client/env/{environmentUUID}/feature-configs".format(
        client.base_url, environmentUUID=environment_uuid
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
    **params: Any
) -> Response[List[FeatureConfig]]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        **params
    )

    retryer = Retrying(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_all(
            retry_if_result(lambda r: r.status_code != 200),
            retry_if_result(handle_http_result)
        ),
        before_sleep=lambda retry_state: warning_fetch_all_features_retrying(
            retry_state.attempt_number,
            retry_state.outcome.result()),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    )

    response = retryer(httpx.get, **kwargs)

    return _build_response(response=response)


def handle_http_result(response):
    code = response.status_code
    if code in RETRYABLE_CODES:
        return True
    else:
        # TODO - revisit these error logs, we need to log the SDK code, but
        # do we want to do it here, or by the caller?
        log.error(
            f'Fetching all features received code #{code} and '
            'will not retry')
        return False



def sync(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Optional[List[FeatureConfig]]:
    """All feature flags with activations in project environment"""

    return sync_detailed(
        client=client,
        environment_uuid=environment_uuid,
        **params
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Response[List[FeatureConfig]]:
    kwargs = _get_kwargs(
        client=client,
        environment_uuid=environment_uuid,
        **params
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    environment_uuid: str,
    **params: Any
) -> Optional[List[FeatureConfig]]:
    """All feature flags with activations in project environment"""

    return (
        await asyncio_detailed(
            client=client,
            environment_uuid=environment_uuid,
            **params
        )
    ).parsed
