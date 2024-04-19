from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.clause import Clause


T = TypeVar("T", bound="GroupServingRule")


@_attrs_define
class GroupServingRule:
    """The rule used to determine what variation to serve to a target

    Attributes:
        rule_id (str): The unique identifier for this rule
        priority (int): The rules priority relative to other rules.  The rules are evaluated in order with 1 being the
            highest Example: 1.
        clauses (List['Clause']): A list of clauses to use in the rule
    """

    rule_id: str
    priority: int
    clauses: List["Clause"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rule_id = self.rule_id

        priority = self.priority

        clauses = []
        for clauses_item_data in self.clauses:
            clauses_item = clauses_item_data.to_dict()
            clauses.append(clauses_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ruleId": rule_id,
                "priority": priority,
                "clauses": clauses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.clause import Clause

        d = src_dict.copy()
        rule_id = d.pop("ruleId")

        priority = d.pop("priority")

        clauses = []
        _clauses = d.pop("clauses")
        for clauses_item_data in _clauses:
            clauses_item = Clause.from_dict(clauses_item_data)

            clauses.append(clauses_item)

        group_serving_rule = cls(
            rule_id=rule_id,
            priority=priority,
            clauses=clauses,
        )

        group_serving_rule.additional_properties = d
        return group_serving_rule

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
