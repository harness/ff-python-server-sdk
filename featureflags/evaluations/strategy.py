import mmh3

from .constants import ONE_HUNDRED


def get_normalized_number(identifier: str, bucket_by: str) -> int:
    return get_normalized_number_with_normalizer(identifier, bucket_by,
                                                 ONE_HUNDRED)


def get_normalized_number_with_normalizer(
    identifier: str, bucket_by: str, normalizer: int
) -> int:
    value = ":".join([bucket_by, identifier])
    hash = int(mmh3.hash(value))
    return (hash % normalizer) + 1
