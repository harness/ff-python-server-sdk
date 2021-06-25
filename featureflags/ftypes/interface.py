import abc
import typing


class Interface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "starts_with")
            and callable(subclass.starts_with)
            and hasattr(subclass, "ends_with")
            and callable(subclass.ends_with)
            and hasattr(subclass, "match")
            and callable(subclass.match)
            and hasattr(subclass, "contains")
            and callable(subclass.contains)
            and hasattr(subclass, "equal_sensitive")
            and callable(subclass.equal_sensitive)
            and hasattr(subclass, "equal")
            and callable(subclass.equal)
            and hasattr(subclass, "greater_than")
            and callable(subclass.greater_than)
            and hasattr(subclass, "greater_than_equal")
            and callable(subclass.greater_than_equal)
            and hasattr(subclass, "less_than")
            and callable(subclass.less_than)
            and hasattr(subclass, "less_than_equal")
            and callable(subclass.less_than_equal)
            and hasattr(subclass, "in_list")
            and callable(subclass.in_list)
            or NotImplemented
        )

    @abc.abstractmethod
    def starts_with(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def ends_with(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def match(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def contains(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def equal_sensitive(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def equal(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def greater_than(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def greater_than_equal(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def less_than(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def less_than_equal(self, value: typing.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def in_list(self, value: typing.List[typing.Any]) -> bool:
        raise NotImplementedError
