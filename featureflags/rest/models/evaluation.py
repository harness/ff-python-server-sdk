from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.evaluation_value import EvaluationValue
from ..types import Unset

T = TypeVar("T", bound="Evaluation")


@attr.s(auto_attribs=True)
class Evaluation:
    """  """

    flag: str
    value: Union[bool, str, int, EvaluationValue]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        flag = self.flag
        if isinstance(self.value, EvaluationValue):
            value = self.value.to_dict()

        else:
            value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "flag": flag,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        flag = d.pop("flag")

        def _parse_value(data: Any) -> Union[bool, str, int, EvaluationValue]:
            data = None if isinstance(data, Unset) else data
            value: Union[bool, str, int, EvaluationValue]
            try:
                value = EvaluationValue.from_dict(data)

                return value
            except:  # noqa: E722
                pass
            return cast(Union[bool, str, int, EvaluationValue], data)

        value = _parse_value(d.pop("value"))

        evaluation = cls(
            flag=flag,
            value=value,
        )

        evaluation.additional_properties = d
        return evaluation

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
