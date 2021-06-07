from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.clause import Clause
from ..models.serve import Serve

T = TypeVar("T", bound="ServingRule")


@attr.s(auto_attribs=True)
class ServingRule:
    """  """

    rule_id: str
    priority: int
    clauses: List[Clause]
    serve: Serve
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rule_id = self.rule_id
        priority = self.priority
        clauses = []
        for clauses_item_data in self.clauses:
            clauses_item = clauses_item_data.to_dict()

            clauses.append(clauses_item)

        serve = self.serve.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ruleId": rule_id,
                "priority": priority,
                "clauses": clauses,
                "serve": serve,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        rule_id = d.pop("ruleId")

        priority = d.pop("priority")

        clauses = []
        _clauses = d.pop("clauses")
        for clauses_item_data in _clauses:
            clauses_item = Clause.from_dict(clauses_item_data)

            clauses.append(clauses_item)

        serve = Serve.from_dict(d.pop("serve"))

        serving_rule = cls(
            rule_id=rule_id,
            priority=priority,
            clauses=clauses,
            serve=serve,
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
