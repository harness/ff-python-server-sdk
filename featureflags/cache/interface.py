import abc
import typing


class Interface(metaclass=abc.ABCMeta):
    
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get') and
                callable(subclass.get) and
                hasattr(subclass, 'set') and
                callable(subclass.set) and
                hasattr(subclass, 'remove') and
                callable(subclass.remove) or
                NotImplemented)

    @abc.abstractmethod
    def get(self, key: str) -> typing.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, value: typing.Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, keys: typing.List[str]) -> None:
        raise NotImplementedError