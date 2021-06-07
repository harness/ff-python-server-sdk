import attr


@attr.s(auto_attribs=True)
class Tag(object):
    name: str
    value: str

