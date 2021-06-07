import json
import typing

import attr

from featureflags.evaluation.enum import FeatureState, Kind
from featureflags.evaluation.clause import Clauses
from featureflags.evaluation.strategy import get_normalized_number
from featureflags.evaluation.constants import ONE_HUNDRED
from featureflags.evaluation.target import Target

from .segment import Segments
from .variation import Variation


@attr.s(auto_attribs=True)
class Evaluation(object):
    flag: str
    variation: typing.Optional[Variation] = None


@attr.s(auto_attribs=True)
class WeightedVariation(object):
    variation: str
    weight: int


@attr.s(auto_attribs=True)
class Distribution(object):
    bucket_by: str
    variations: typing.List[WeightedVariation]

    def get_key_name(self, target: Target) -> str:
        variation: str = ''
        for _variation in self.variations:
            variation = _variation.variation
            if self.is_enabled(target, _variation.weight):
                return variation
        if self.is_enabled(target, ONE_HUNDRED):
            return variation
        return ''

    def is_enabled(self, target: Target, percentage: int) -> bool:
        identifier = target.get_attr_value(self.bucket_by)
        if not identifier or identifier == '':
            return False
        bucket_id = get_normalized_number(identifier, self.bucket_by)
        return percentage > 0 and bucket_id <= percentage


@attr.s(auto_attribs=True)
class Serve(object):
    distribution: typing.Optional[Distribution] = None
    variation: typing.Optional[str] = None


@attr.s(auto_attribs=True)
class Prerequisite(object):
    feature: str
    variations: typing.List[str]


@attr.s(auto_attribs=True)
class ServingRule(object):
    clauses: Clauses
    priority: int
    rule_id: str
    serve: Serve


class ServingRules(typing.List[ServingRule]):

    def get_variation_name(self, target: Target,
                           segments: typing.Optional[Segments] = None,
                           default_serve: typing.Optional[Serve] = None) -> typing.Optional[str]:
        for rule in self:
            if not rule.clauses.evaluate(target, segments):
                continue

            if rule.serve.distribution:
                return rule.serve.distribution.get_key_name(target)

            if rule.serve.variation:
                return rule.serve.variation

        if default_serve:
            if default_serve.variation:
                return default_serve.variation

            if default_serve.distribution:
                return default_serve.distribution.get_key_name(target)

        return None


@attr.s(auto_attribs=True)
class VariationMap(object):
    target_segments: typing.List[str]
    targets: typing.List[str]
    variation: str


@attr.s(auto_attribs=True)
class FeatureConfig(object):

    default_serve: Serve
    environment: str
    feature: str
    kind: str
    off_variation: str
    project: str
    state: FeatureState
    variations: typing.List[Variation]
    rules: ServingRules = ServingRules()
    segments: typing.Optional[Segments] = None
    prerequisites: typing.Optional[typing.List[Prerequisite]] = None
    variation_to_target_map: typing.Optional[typing.List[VariationMap]] = None

    def evaluate(self, target: Target) -> Evaluation:
        variation = None
        if self.kind == Kind.BOOLEAN:
            variation = self.bool_variation(target)
        return Evaluation(flag=self.feature, variation=variation)

    def bool_variation(self, target: Target) -> typing.Optional[Variation]:
        if self.kind != Kind.BOOLEAN:
            return None
        return self.get_variation(target)

    def get_variation_name(self, target: Target) -> typing.Optional[str]:
        if self.state == FeatureState.OFF:
            return self.off_variation

        if self.variation_to_target_map:
            for variation_map in self.variation_to_target_map:
                for _target in variation_map.targets:
                    if target.identifier == _target:
                        return variation_map.variation

        return self.rules.get_variation_name(target, self.segments, self.default_serve)

    def get_variation(self, target: Target) -> typing.Optional[Variation]:
        identifier = self.get_variation_name(target)
        variation = next((val for val in self.variations
                          if val.identifier == identifier), None)
        return variation
