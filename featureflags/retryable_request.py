from tenacity import retry_if_result, wait_exponential, \
    stop_after_attempt, retry, retry_if_exception_type
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
from .sdk_logging_codes import warn_auth_retying, \
    warning_fetch_all_segments_retrying, warning_fetch_all_features_retrying, \
    warning_fetch_feature_by_id_retrying, warning_fetch_group_by_id_retrying

# TODO change to 10
MAX_RETRY_ATTEMPTS = 2

RETRYABLE_CODES = {HTTPStatus.BAD_GATEWAY, HTTPStatus.NOT_FOUND,
                   HTTPStatus.INTERNAL_SERVER_ERROR}


class UnrecoverableRequestException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def __str__(self):
        return f'Request failed with unrecoverable error: ' \
               f'status_code={self.status_code}, contents={self.content}'


def default_retry_strategy(before_sleep_func=None, on_retry_error=None):
    return retry(
        retry=(
                retry_if_result(handle_http_result) |
                retry_if_exception_type(UnexpectedStatus)),

        wait=wait_exponential(multiplier=1, max=10),
        before_sleep=before_sleep_func,
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        retry_error_callback=lambda response: on_retry_error(
            response),

    )


def handle_http_result(response):
    code = response.status_code
    if code == HTTPStatus.OK:
        return False

    if code in RETRYABLE_CODES:
        return True
    else:
        raise Exception(
            f'Request failed with unrecoverable error: status_code='
            f'{response.status_code}, content={response.content}')


def handle_retries_exceeded(retry_state):
    content = retry_state.outcome.result().content
    if content == b'':
        content = ""
    raise UnrecoverableRequestException(
        retry_state.outcome.result().status_code,
        content)


@default_retry_strategy(
    before_sleep_func=lambda retry_state: warn_auth_retying(
        retry_state.attempt_number,
        retry_state.outcome.result()),
    on_retry_error=handle_retries_exceeded)
def retryable_authenticate(
        client: Union[AuthenticatedClient, Client],
        body: AuthenticationRequest) -> \
        Response[Union[AuthenticationResponse, Any]]:
    response = authenticate(client=client, body=body)
    return response


@default_retry_strategy(
    before_sleep_func=lambda retry_state: warning_fetch_all_segments_retrying(
        retry_state.attempt_number,
        retry_state.outcome.result()),
    on_retry_error=handle_retries_exceeded)
def retryable_retrieve_segments(environment_uuid: str,
                                client: AuthenticatedClient,
                                cluster: Union[Unset, str] = UNSET) -> \
        Response[list[Segment]]:
    return retrieve_segments(client=client,
                             environment_uuid=environment_uuid,
                             cluster=cluster)


@default_retry_strategy(
    before_sleep_func=lambda retry_state: warning_fetch_all_features_retrying(
        retry_state.attempt_number,
        retry_state.outcome.result()),
    on_retry_error=handle_retries_exceeded)
def retryable_retrieve_feature_config(environment_uuid: str,
                                      client: AuthenticatedClient,
                                      cluster: Union[Unset, str] = UNSET) -> \
        Response[list[FeatureConfig]]:
    return retrieve_flags(client=client,
                          environment_uuid=environment_uuid,
                          cluster=cluster)


@default_retry_strategy(
    before_sleep_func=lambda retry_state: warning_fetch_feature_by_id_retrying(
        retry_state.attempt_number,
        retry_state.outcome.result()))
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


@default_retry_strategy(
    before_sleep_func=lambda retry_state: warning_fetch_group_by_id_retrying(
        retry_state.attempt_number,
        retry_state.outcome.result()))
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
