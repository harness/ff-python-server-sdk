
class Unset:
    def __bool__(self) -> bool:
        return False


UNSET: Unset = Unset()
