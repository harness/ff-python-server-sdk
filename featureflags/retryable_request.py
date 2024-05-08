from tenacity import retry_if_result, wait_exponential, \
    stop_after_attempt, retry
from http import HTTPStatus
from typing import Any, Optional, Union

from .openapi.config.api.client.authenticate import \
    sync_detailed as authenticate
from .openapi.config.api.client.get_all_segments import \
    sync_detailed as retrieve_segments
from .openapi.config.api.client.get_feature_config import \
    sync_detailed as retrieve_flags
from .openapi.config.api.client.get_feature_config_by_identifier import \
    sync_detailed as retrieve_flag_by_identifier
from .openapi.config.api.client.get_segment_by_identifier import \
    sync_detailed as retrieve_segment_by_identifier
from .openapi.config.models import AuthenticationRequest, \
    AuthenticationResponse

from featureflags.openapi.config import AuthenticatedClient, Client
from featureflags.openapi.config.types import Unset, UNSET, Response
from .openapi.config.errors import UnexpectedStatus
from .openapi.config.models import Segment, FeatureConfig
from .sdk_logging_codes import warn_auth_retying

# TODO change to 10
MAX_RETRY_ATTEMPTS = 2


def default_retry_strategy(before_sleep_func=None):
    return retry(
        retry=(
            retry_if_result(
                lambda response: response.status_code in [
                    HTTPStatus.BAD_GATEWAY, HTTPStatus.NOT_FOUND,
                    HTTPStatus.INTERNAL_SERVER_ERROR, UnexpectedStatus,
                    HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED])),
        wait=wait_exponential(multiplier=1, max=10),
        before_sleep=before_sleep_func,
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    )


@default_retry_strategy(
    before_sleep_func=lambda retry_state: warn_auth_retying(
        retry_state.attempt_number,
        retry_state.outcome.result()))
def retryable_authenticate(
        client: Union[AuthenticatedClient, Client],
        body: AuthenticationRequest) -> \
        Response[Union[AuthenticationResponse, Any]]:
    return authenticate(client=client, body=body)


@default_retry_strategy()
def retryable_retrieve_segments(environment_uuid: str,
                                client: AuthenticatedClient,
                                cluster: Union[Unset, str] = UNSET) -> \
        Response[list[Segment]]:
    return retrieve_segments(client=client,
                             environment_uuid=environment_uuid,
                             cluster=cluster)


@default_retry_strategy()
def retryable_retrieve_feature_config(environment_uuid: str,
                                      client: AuthenticatedClient,
                                      cluster: Union[Unset, str] = UNSET) -> \
        Response[list[FeatureConfig]]:
    return retrieve_flags(client=client,
                          environment_uuid=environment_uuid,
                          cluster=cluster)


@default_retry_strategy()
def retryable_retrieve_feature_config_by_identifier(environment_uuid: str,
                                                    identifier: str,
                                                    client:
                                                    AuthenticatedClient,
                                                    cluster: Union[
                                                        Unset, str] = UNSET) \
        -> Response[FeatureConfig]:
    return retrieve_flag_by_identifier(client=client,
                                       identifier=identifier,
                                       environment_uuid=environment_uuid,
                                       cluster=cluster)


@default_retry_strategy()
def retryable_retrieve_segment_by_identifier(environment_uuid: str,
                                             identifier: str,
                                             client:
                                             AuthenticatedClient,
                                             cluster: Union[
                                                 Unset, str] = UNSET) \
        -> Optional[Union[Any, Segment]]:
    return retrieve_segment_by_identifier(client=client,
                                          identifier=identifier,
                                          environment_uuid=environment_uuid,
                                          cluster=cluster)
