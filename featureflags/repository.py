import abc
from typing import List, Optional

from featureflags.evaluations.constants import SEGMENT_MATCH_OPERATOR
from featureflags.interface import Cache, Store
from featureflags.openapi.config.models.feature_config import FeatureConfig
from featureflags.openapi.config.models.segment import Segment
from featureflags.openapi.config.types import Unset
from featureflags.util import log


class QueryInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_flag') and
                callable(subclass.get_flag) and
                hasattr(subclass, 'get_segment') and
                callable(subclass.get_segment) or
                hasattr(subclass, 'find_flags_by_segment') and
                callable(subclass.find_flags_by_segment) or
                NotImplemented)

    @abc.abstractmethod
    def get_flag(self, identifier: str) -> Optional[FeatureConfig]:
        """Get flag from repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_segment(self, identifier: str) -> Optional[Segment]:
        """Get Target group from repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def find_flags_by_segment(self, identifier: str) -> List[str]:
        """Find all flags with rule segment match"""
        raise NotImplementedError


class DataProviderInterface(QueryInterface):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_flag') and
                callable(subclass.get_flag) and
                hasattr(subclass, 'get_segment') and
                callable(subclass.get_segment) or
                hasattr(subclass, 'close') and
                callable(subclass.close) or
                NotImplemented)

    @abc.abstractmethod
    def set_flag(self, flag: FeatureConfig) -> None:
        """Put flag to the repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_segment(self, group: Segment) -> None:
        """Put Target group to the repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def remove_flag(self, identifier: str) -> None:
        """Remove Flag from the repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def remove_segment(self, identifier: str) -> None:
        """Remove Target group from the repository"""
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Put Target group to the repository"""
        raise NotImplementedError


class Repository(DataProviderInterface):

    def __init__(self, cache: Cache, store: Store = None) -> None:
        self.cache = cache
        self.store = store

    def get_flag(self, identifier: str,
                 cacheable: bool = None, is_outdated_check=False) -> \
            Optional[FeatureConfig]:
        flag_key = format_flag_key(identifier)
        try:
            flag = self.cache.get(flag_key)
            log.debug("return flag from cache %s", identifier)
            return flag
        except KeyError:
            if self.store:
                flag = self.store.get(flag_key)
                log.debug("return flag from store %s", identifier)
                if flag and cacheable:
                    log.debug("set flag to the cache %s", identifier)
                    self.cache.set(flag_key, flag)
                return flag
        # If we are checking if a flag is outdated, it might not be in the
        # cache to start with, so don't log a warning here
        if not is_outdated_check:
            log.warning("flag not found %s", identifier)
        return None

    def get_segment(self, identifier: str,
                    cacheable: bool = None, is_outdated_check=False) -> \
            Optional[Segment]:
        segment_key = format_segment_key(identifier)
        try:
            segment = self.cache.get(segment_key)
            log.debug("return segment from cache %s", identifier)
            return segment
        except KeyError:
            if self.store:
                segment = self.store.get(segment_key)
                log.debug("return segment from store %s", identifier)
                if segment and cacheable:
                    log.debug("set segment to the cache %s", identifier)
                    self.cache.set(segment_key, segment)
                return segment
        # If we are checking if a segment is outdated, it might not be in the
        # cache to start with, so don't log a warning here
        if not is_outdated_check:
            log.warning("segment not found %s", identifier)
        return None

    def set_flag(self, flag: FeatureConfig) -> None:
        if self.is_flag_outdated(flag.feature, flag):
            log.debug("Flag %s already exists", flag.feature)
            return None

        flag_key = format_flag_key(flag.feature)

        if self.store:
            self.store.set(flag_key, flag)
            self.cache.remove([flag_key])
            log.debug(
                "Flag %s successfully stored and cache invalidated",
                flag.feature)
        else:
            self.cache.set(flag_key, flag)
            log.debug("Flag %s successfully cached", flag.feature)

    def set_segment(self, segment: Segment) -> None:
        if self.is_segment_outdated(segment.identifier, segment):
            log.debug("Segment %s already exists", segment.identifier)
            return None

        segment_key = format_segment_key(segment.identifier)

        if self.store:
            self.store.set(segment_key, segment)
            self.cache.remove([segment_key])
            log.debug(
                "Segment %s successfully stored and cache invalidated",
                segment.identifier)
        else:
            self.cache.set(segment_key, segment)
            log.debug("Segment %s successfully cached", segment.identifier)

    def find_flags_by_segment(self, segment: str) -> List[str]:
        result = []
        keys = self.cache.keys()
        if self.store:
            keys = self.store.keys()
        for key in keys:
            flag = self.get_flag(key, cacheable=False)
            if not flag:
                continue
            for serving_rule in flag.rules:
                for clause in serving_rule.clauses:
                    if clause.op == SEGMENT_MATCH_OPERATOR and not next(
                            (val for val in clause.values if val == segment),
                            None
                    ):
                        log.debug("Flag %s evaluated in segments",
                                  flag.feature)
                        result.append(flag.feature)
        return result

    def remove_flag(self, identifier: str) -> None:
        """Remove Flag from the repository"""
        flag_key = format_flag_key(identifier)
        if self.store:
            self.store.remove([flag_key])
            log.debug("Flag %s successfully deleted from store", identifier)

        self.cache.remove([flag_key])
        log.debug("Flag %s successfully deleted from cache", identifier)

    def remove_segment(self, identifier: str) -> None:
        """Remove Target group from the repository"""
        segment_key = format_segment_key(identifier)
        if self.store:
            self.store.remove([segment_key])
            log.debug("Segment %s successfully deleted from store", identifier)

        self.cache.remove([segment_key])
        log.debug("Segment %s successfully deleted from cache", identifier)

    def close(self) -> None:
        if self.store:
            self.store.close()

    def is_flag_outdated(self, identifier: str,
                         new_config: FeatureConfig) -> bool:
        flag = self.get_flag(identifier, cacheable=False,
                             is_outdated_check=True)
        if flag and not isinstance(flag.version, Unset) and \
                not isinstance(new_config, Unset) and \
                not isinstance(new_config.version, Unset):
            return flag.version >= new_config.version
        return False

    def is_segment_outdated(self, identifier: str,
                            new_segment: Segment) -> bool:
        segment = self.get_segment(identifier, cacheable=False,
                                   is_outdated_check=True)
        if segment and not isinstance(segment.version, Unset) and \
                not isinstance(new_segment, Unset) and \
                not isinstance(new_segment.version, Unset):
            return segment.version >= new_segment.version
        return False


def format_flag_key(identifier: str) -> str:
    return f'flags/{identifier}'


def format_segment_key(identifier: str) -> str:
    return f'segments/{identifier}'
