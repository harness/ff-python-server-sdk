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

TARGET_SEGMENT_RULES_PARAM = "v2"


class UnrecoverableRequestException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def __str__(self):
        return f'Request failed with unrecoverable error: ' \
               f'status_code={self.status_code}, contents={self.content}'


def default_retry_strategy(before_sleep_func=None, on_retry_error=None):
    max_retry_attempts = 10
    return retry(
        retry=(
                retry_if_result(handle_http_result) |
                retry_if_exception_type(UnexpectedStatus)),

        wait=wait_exponential(multiplier=1, max=10),
        before_sleep=before_sleep_func,
        stop=stop_after_attempt(max_retry_attempts),
        retry_error_callback=lambda response: on_retry_error(
            response),
    )


def handle_http_result(response):
    retryable_codes = {HTTPStatus.BAD_GATEWAY, HTTPStatus.NOT_FOUND,
                       HTTPStatus.INTERNAL_SERVER_ERROR}
    code = response.status_code
    if code == HTTPStatus.OK:
        return False

    if code in retryable_codes:
        return True
    else:
        raise UnrecoverableRequestException(response.status_code,
                                            response.content)


def handle_retries_exceeded(retry_state):
    content = retry_state.outcome.result().content
    if content == b'':
        content = ""
    raise UnrecoverableRequestException(
        retry_state.outcome.result().status_code,
        content)


def make_log_warning_before_sleep(warning_fun):
    def log_warning_before_sleep(retry_state):
        error_message = build_retry_warning_message(retry_state)
        warning_fun(retry_state.attempt_number, error_message)

    return log_warning_before_sleep


def build_retry_warning_message(retry_state):
    # Defensive check in case getting result of outcome throws
    try:
        result = retry_state.outcome.result()
        status_code = result.status_code
        content = result.content if result.content != b'' else ""
        error_message = f"status_code={status_code}, content={content}"
    except Exception as e:
        status_code = None
        content = str(e)
        error_message = f"status_code={status_code}, content={content}"
    return error_message


@default_retry_strategy(
    before_sleep_func=make_log_warning_before_sleep(warn_auth_retying),
    on_retry_error=handle_retries_exceeded)
def retryable_authenticate(
        client: Union[AuthenticatedClient, Client],
        body: AuthenticationRequest) -> \
        Response[Union[AuthenticationResponse, Any]]:
    response = authenticate(client=client, body=body)
    return response


@default_retry_strategy(
    before_sleep_func=make_log_warning_before_sleep(
        warning_fetch_all_segments_retrying),
    on_retry_error=handle_retries_exceeded)
def retryable_retrieve_segments(environment_uuid: str,
                                client: AuthenticatedClient,
                                cluster: Union[Unset, str] = UNSET) -> \
        Response[list[Segment]]:
    return retrieve_segments(client=client,
                             environment_uuid=environment_uuid,
                             cluster=cluster,
                             rules=TARGET_SEGMENT_RULES_PARAM)


@default_retry_strategy(
    before_sleep_func=make_log_warning_before_sleep(
        warning_fetch_all_features_retrying),
    on_retry_error=handle_retries_exceeded)
def retryable_retrieve_feature_config(environment_uuid: str,
                                      client: AuthenticatedClient,
                                      cluster: Union[Unset, str] = UNSET) -> \
        Response[list[FeatureConfig]]:
    return retrieve_flags(client=client,
                          environment_uuid=environment_uuid,
                          cluster=cluster)


@default_retry_strategy(
    before_sleep_func=make_log_warning_before_sleep(
        warning_fetch_feature_by_id_retrying),
    on_retry_error=handle_retries_exceeded)
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
    before_sleep_func=make_log_warning_before_sleep(
        warning_fetch_group_by_id_retrying),
    on_retry_error=handle_retries_exceeded)
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
                                          cluster=cluster,
                                          rules=TARGET_SEGMENT_RULES_PARAM)
