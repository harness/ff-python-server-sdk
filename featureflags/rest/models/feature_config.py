from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.feature_config_kind import FeatureConfigKind
from ..models.feature_state import FeatureState
from ..models.prerequisite import Prerequisite
from ..models.serve import Serve
from ..models.serving_rule import ServingRule
from ..models.variation import Variation
from ..models.variation_map import VariationMap
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureConfig")


@attr.s(auto_attribs=True)
class FeatureConfig:
    """  """

    project: str
    environment: str
    feature: str
    state: FeatureState
    kind: FeatureConfigKind
    variations: List[Variation]
    default_serve: Serve
    off_variation: str
    rules: Union[Unset, List[ServingRule]] = UNSET
    prerequisites: Union[Unset, List[Prerequisite]] = UNSET
    variation_to_target_map: Union[Unset, List[VariationMap]] = UNSET
    version: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project
        environment = self.environment
        feature = self.feature
        state = self.state.value

        kind = self.kind.value

        variations = []
        for variations_item_data in self.variations:
            variations_item = variations_item_data.to_dict()

            variations.append(variations_item)

        default_serve = self.default_serve.to_dict()

        off_variation = self.off_variation
        rules: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.rules, Unset):
            rules = []
            for rules_item_data in self.rules:
                rules_item = rules_item_data.to_dict()

                rules.append(rules_item)

        prerequisites: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.prerequisites, Unset):
            prerequisites = []
            for prerequisites_item_data in self.prerequisites:
                prerequisites_item = prerequisites_item_data.to_dict()

                prerequisites.append(prerequisites_item)

        variation_to_target_map: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.variation_to_target_map, Unset):
            variation_to_target_map = []
            for variation_to_target_map_item_data in self.variation_to_target_map:
                variation_to_target_map_item = (
                    variation_to_target_map_item_data.to_dict()
                )

                variation_to_target_map.append(variation_to_target_map_item)

        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "environment": environment,
                "feature": feature,
                "state": state,
                "kind": kind,
                "variations": variations,
                "defaultServe": default_serve,
                "offVariation": off_variation,
            }
        )
        if rules is not UNSET:
            field_dict["rules"] = rules
        if prerequisites is not UNSET:
            field_dict["prerequisites"] = prerequisites
        if variation_to_target_map is not UNSET:
            field_dict["variationToTargetMap"] = variation_to_target_map
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        project = d.pop("project")

        environment = d.pop("environment")

        feature = d.pop("feature")

        state = FeatureState(d.pop("state"))

        kind = FeatureConfigKind(d.pop("kind"))

        variations = []
        _variations = d.pop("variations")
        for variations_item_data in _variations:
            variations_item = Variation.from_dict(variations_item_data)

            variations.append(variations_item)

        default_serve = Serve.from_dict(d.pop("defaultServe"))

        off_variation = d.pop("offVariation")

        rules = []
        _rules = d.pop("rules", UNSET)
        for rules_item_data in _rules or []:
            rules_item = ServingRule.from_dict(rules_item_data)

            rules.append(rules_item)

        prerequisites = []
        _prerequisites = d.pop("prerequisites", UNSET)
        for prerequisites_item_data in _prerequisites or []:
            prerequisites_item = Prerequisite.from_dict(prerequisites_item_data)

            prerequisites.append(prerequisites_item)

        variation_to_target_map = []
        _variation_to_target_map = d.pop("variationToTargetMap", UNSET)
        for variation_to_target_map_item_data in _variation_to_target_map or []:
            variation_to_target_map_item = VariationMap.from_dict(
                variation_to_target_map_item_data
            )

            variation_to_target_map.append(variation_to_target_map_item)

        version = d.pop("version", UNSET)

        feature_config = cls(
            project=project,
            environment=environment,
            feature=feature,
            state=state,
            kind=kind,
            variations=variations,
            default_serve=default_serve,
            off_variation=off_variation,
            rules=rules,
            prerequisites=prerequisites,
            variation_to_target_map=variation_to_target_map,
            version=version,
        )

        feature_config.additional_properties = d
        return feature_config

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
