from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.clause import Clause
    from ..models.serve import Serve


T = TypeVar("T", bound="ServingRule")


@_attrs_define
class ServingRule:
    """The rule used to determine what variation to serve to a target

    Attributes:
        priority (int): The rules priority relative to other rules.  The rules are evaluated in order with 1 being the
            highest Example: 1.
        clauses (List['Clause']): A list of clauses to use in the rule
        serve (Serve): Describe the distribution rule and the variation that should be served to the target
        rule_id (Union[Unset, str]): The unique identifier for this rule
    """

    priority: int
    clauses: List["Clause"]
    serve: "Serve"
    rule_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        priority = self.priority

        clauses = []
        for clauses_item_data in self.clauses:
            clauses_item = clauses_item_data.to_dict()
            clauses.append(clauses_item)

        serve = self.serve.to_dict()

        rule_id = self.rule_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "priority": priority,
                "clauses": clauses,
                "serve": serve,
            }
        )
        if rule_id is not UNSET:
            field_dict["ruleId"] = rule_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.clause import Clause
        from ..models.serve import Serve

        d = src_dict.copy()
        priority = d.pop("priority")

        clauses = []
        _clauses = d.pop("clauses")
        for clauses_item_data in _clauses:
            clauses_item = Clause.from_dict(clauses_item_data)

            clauses.append(clauses_item)

        serve = Serve.from_dict(d.pop("serve"))

        rule_id = d.pop("ruleId", UNSET)

        serving_rule = cls(
            priority=priority,
            clauses=clauses,
            serve=serve,
            rule_id=rule_id,
        )

        serving_rule.additional_properties = d
        return serving_rule

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
