import typing

import attr

if typing.TYPE_CHECKING:
	from .clause import Clauses
from .target import Target
from .tag import Tag


@attr.s(auto_attribs=True)
class Segment(object):
	identifier: str
	name: str

	created_at: int
	modified_at: int
	environment: str

	excluded: typing.List[str]
	included: typing.List[str]

	rules: 'Clauses'
	tags: typing.List[Tag]
	version: int


class Segments(typing.Dict[str, Segment]):

	def evaluate(self, target: Target) -> bool:
		return True
