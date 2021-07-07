from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from featureflags.models import UNSET, Unset
from featureflags.util import log

from .auth_target import Target
from .constants import SEGMENT_MATCH_OPERATOR
from .enum import FeatureState
from .prerequisite import Prerequisite
from .segment import Segments
from .serve import Serve
from .serving_rule import ServingRule, ServingRules
from .variation import Variation
from .variation_map import VariationMap

T = TypeVar("T", bound="FeatureConfig")


@attr.s(auto_attribs=True)
class Evaluation(object):
    flag: str
    variation: Optional[Variation] = None


class FeatureConfigKind(str, Enum):
    BOOLEAN = "boolean"
    INT = "int"
    NUMBER = "number"
    STRING = "string"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)


@attr.s(auto_attribs=True)
class FeatureConfig(object):

    default_serve: Serve
    environment: str
    feature: str
    kind: FeatureConfigKind
    off_variation: str
    project: str
    state: FeatureState
    variations: List[Variation]
    rules: ServingRules = ServingRules()
    segments: Optional[Segments] = None
    prerequisites: Union[Unset, List[Prerequisite]] = UNSET
    variation_to_target_map: Union[Unset, List[VariationMap]] = UNSET
    version: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    cache: Dict[str, Any] = {}

    def evaluate(self, target: Target) -> Evaluation:
        log.debug('Flag kind: %s', self.kind)
        variation = None
        if self.kind == FeatureConfigKind.BOOLEAN:
            variation = self.bool_variation(target)
        return Evaluation(flag=self.feature, variation=variation)

    def bool_variation(self, target: Target) -> Optional[Variation]:
        if self.kind != FeatureConfigKind.BOOLEAN:
            return None
        return self.get_variation(target)

    def int_variation(self, target: Target) -> Optional[Variation]:
        if self.kind != FeatureConfigKind.INT:
            return None
        return self.get_variation(target)

    def number_variation(self, target: Target) -> Optional[Variation]:
        if self.kind != FeatureConfigKind.NUMBER:
            return None
        return self.get_variation(target)

    def string_variation(self, target: Target) -> Optional[Variation]:
        if self.kind != FeatureConfigKind.STRING:
            return None
        return self.get_variation(target)

    def get_variation_name(self, target: Target) -> Optional[str]:
        if self.state == FeatureState.OFF:
            return self.off_variation

        if not isinstance(self.variation_to_target_map, Unset):
            for variation_map in self.variation_to_target_map:
                if not isinstance(variation_map.targets, Unset):
                    for _target in variation_map.targets:
                        if target.identifier == _target.identifier:
                            return variation_map.variation

        return self.rules.get_variation_name(target, self.segments,
                                             self.default_serve)

    def get_variation(self, target: Target) -> Optional[Variation]:
        identifier = self.get_variation_name(target)
        variation = next(
            (val for val in self.variations if val.identifier == identifier),
            None
        )
        return variation

    def get_segment_identifiers(self) -> List[str]:
        if 'segments' in self.cache:
            return self.cache['segments']
        identifiers: List[str] = []
        for rule in self.rules:
            for clause in rule.clauses:
                if clause.op == SEGMENT_MATCH_OPERATOR:
                    for identifier in clause.values:
                        identifiers.append(identifier)
        self.cache['segments'] = identifiers
        return identifiers

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
        rules: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.rules, Unset):
            rules = []
            for rules_item_data in self.rules:
                rules_item = rules_item_data.to_dict()

                rules.append(rules_item)

        prerequisites: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.prerequisites, Unset):
            prerequisites = []
            for prerequisites_item_data in self.prerequisites:
                prerequisites_item = prerequisites_item_data.to_dict()

                prerequisites.append(prerequisites_item)

        variation_to_target_map: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.variation_to_target_map, Unset):
            variation_to_target_map = []
            for variation_to_target_map_item_data in \
                    self.variation_to_target_map:
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

        rules: ServingRules = ServingRules()
        _rules = d.pop("rules", UNSET)
        for rules_item_data in _rules or []:
            rules_item = ServingRule.from_dict(rules_item_data)

            rules.append(rules_item)

        prerequisites = []
        _prerequisites = d.pop("prerequisites", UNSET)
        for prerequisites_item_data in _prerequisites or []:
            prerequisites_item = Prerequisite.from_dict(
                prerequisites_item_data
            )

            prerequisites.append(prerequisites_item)

        variation_to_target_map = []
        _variation_to_target_map = d.pop("variationToTargetMap", UNSET)
        for variation_to_target_map_item_data in \
                _variation_to_target_map or []:
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
