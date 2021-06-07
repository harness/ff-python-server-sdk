import json
import typing

import attr

@attr.s
class Variation(object):
	description: typing.Optional[str]
	identifier: str = attr.ib()
	name: typing.Optional[str]
	value: str = attr.ib()

	def bool(self, default: bool = False) -> bool:
		if self.value:
			return self.value == 'true'
		return default

	def string(self, default: str) -> str:
		return self.value or default

	def number(self, default: float) -> float:
		if self.value:
			return float(self.value)
		return default

	def int(self, default: int) -> int:
		if self.value:
			return int(self.value)
		return default

	def json(self, default: dict) -> dict:
		if self.value:
			return json.loads(self.value)
		return default
