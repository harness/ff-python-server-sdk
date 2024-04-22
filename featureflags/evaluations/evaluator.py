from typing import Dict, List, Optional, Union

import mmh3

from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.constants import (CONTAINS_OPERATOR,
                                                ENDS_WITH_OPERATOR,
                                                EQUAL_OPERATOR,
                                                EQUAL_SENSITIVE_OPERATOR,
                                                GT_OPERATOR, IN_OPERATOR,
                                                ONE_HUNDRED,
                                                SEGMENT_MATCH_OPERATOR,
                                                STARTS_WITH_OPERATOR)
from featureflags.openapi.config.models.clause import Clause
from featureflags.openapi.config.models.distribution import Distribution
from featureflags.openapi.config.models.feature_config import (
    FeatureConfig, FeatureConfigKind)
from featureflags.openapi.config.models.feature_state import FeatureState
from featureflags.openapi.config.models.segment import Segment
from featureflags.openapi.config.models.serve import Serve
from featureflags.openapi.config.models.serving_rule import ServingRule
from featureflags.openapi.config.models.variation import Variation
from featureflags.openapi.config.models.variation_map import VariationMap
from featureflags.openapi.config.types import Unset
from featureflags.repository import QueryInterface
from featureflags.util import log

EMPTY_VARIATION = Variation(identifier="", value=None)


class Segments(Dict[str, Segment]):

    def evaluate(self, target: Target) -> bool:
        for _, segment in self.items():
            if not segment.evaluate(target):
                return False
        return True


class Clauses(List[Clause]):
    def evaluate(self, target: Target, segments: Optional['Segments']) -> bool:
        for clause in self:
            operator = target.get_type(clause.attribute)
            if not clause.evaluate(target, segments, operator):
                return False
        return True


class ServingRules(List[ServingRule]):
    def get_variation_name(
            self,
            target: Target,
            segments: Optional[Segments] = None,
            default_serve: Optional[Serve] = None,
    ) -> Optional[str]:
        for rule in self:
            if not rule.clauses.evaluate(target, segments):
                continue

            if not isinstance(rule.serve.distribution, Unset):
                return rule.serve.distribution.get_key_name(target)

            if not isinstance(rule.serve.variation, Unset):
                return rule.serve.variation

        if default_serve:
            if not isinstance(default_serve.variation, Unset):
                return default_serve.variation

            if not isinstance(default_serve.distribution, Unset):
                return default_serve.distribution.get_key_name(target)
        return None


class FlagKindMismatchException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"FlagKindMismatchException: {self.message}"


class Evaluator(object):

    def __init__(self, provider: QueryInterface):
        self.provider = provider

    def get_kind(self, identifier) -> Optional[FeatureConfigKind]:
        fc = self.provider.get_flag(identifier)
        if not fc:
            return None
        return fc.kind

    def _find_variation(self, variations: List[Variation],
                        identifier: Optional[str]) -> Variation:
        if not identifier:
            log.debug("Empty identifier %s or variations %s occurred",
                      identifier, variations)
            return EMPTY_VARIATION
        variation = next(
            (val for val in variations if val.identifier == identifier),
            EMPTY_VARIATION
        )
        log.debug("Variation %s found in variations %s",
                  identifier, variations)
        return variation

    def _get_normalized_number(self, bucket_by: str, identifier: str):
        value = ":".join([bucket_by, identifier])
        hash = int(mmh3.hash(value, signed=False))
        normalized_number = (hash % ONE_HUNDRED) + 1
        log.debug("MM3 normalized number for %s = %d", value,
                  normalized_number)
        return normalized_number

    def _is_enabled(self, target: Target, bucket_by: str,
                    percentage: int) -> bool:
        attr_value = target.get_attr_value(bucket_by)
        if not attr_value:
            log.debug("Returns False. %s is set to %s", bucket_by, attr_value)
            old_bb = bucket_by
            bucket_by = "identifier"
            attr_value = target.get_attr_value(bucket_by)
            if not attr_value or attr_value == "":
                return False
            log.warning("SDKCODE:6002 BucketBy attribute not found in "
                        "target attributes, falling back to 'identifier':"
                        " missing=%s, using value=%s", old_bb, attr_value)

        bucket_id = self._get_normalized_number(bucket_by, attr_value)
        log.debug("MM3 percentage_check=%d bucket_by=%s value=%s bucket=%d",
                  percentage, bucket_by, attr_value, bucket_id)
        return percentage > 0 and bucket_id <= percentage

    def _evaluate_distribution(self, distribution: Distribution,
                               target: Target) -> Optional[str]:
        variation = None
        if not distribution:
            log.debug("Distribution is empty")
            return variation
        total_percentage = 0
        for _variation in distribution.variations:
            variation = _variation.variation
            log.debug("Checking variation %s", variation)
            total_percentage += _variation.weight
            if self._is_enabled(target, distribution.bucket_by,
                                total_percentage):
                log.debug("Enabled for distribution %s", distribution)
                return variation
        log.debug("Variation of distribution evaluation %s", variation)
        return variation

    def _check_target_in_segment(self, segments: List[str],
                                 target: Target) -> bool:
        for segment_identifier in segments:
            segment = self.provider.get_segment(segment_identifier)

            if segment:
                # Should Target be excluded - if in excluded
                # list we return false
                if not isinstance(segment.excluded, Unset) and \
                        next(
                            (val for val in segment.excluded
                             if val.identifier == target.identifier),
                            None) is not None:
                    log.debug('Target % s excluded from segment % s' +
                              'via exclude list\n',
                              target.name, segment.name)
                    return False

                # Should Target be included - if in included list
                #  we return true
                if not isinstance(segment.included, Unset) and \
                        next(
                            (val for val in segment.included
                             if val.identifier == target.identifier),
                            None) is not None:
                    log.debug('Target %s included in segment %s' +
                              ' via include list\n',
                              target.name, segment.name)
                    return True

                if segment.serving_rules:
                    log.debug('Found and using enhanced serving_rules')
                    # Use enhanced rules first if they're available
                    segment.serving_rules.sort(key=lambda rule: rule.priority)

                    for serving_rule in segment.serving_rules:
                        if self._evaluate_clauses_v2(serving_rule.clauses,
                                                     target):
                            return True

                else:
                    # Fall back to legacy rules
                    # Should Target be included via segment rules
                    if segment.rules and self._evaluate_clauses(segment.rules,
                                                                target):
                        log.debug(
                            'Target %s included in segment %s via rules\n',
                            target.name, segment.name)
                        return True

        log.debug("Target groups empty return false")
        return False

    def _evaluate_clause(self, clause: Clause, target: Target) -> bool:
        if clause.op is None:
            log.debug("Clause is empty")
            return False

        if not clause.values:
            log.debug("Clause values is empty")
            return False

        operator = clause.op.lower()
        type = target.get_type(clause.attribute)

        if type is None:
            if operator == SEGMENT_MATCH_OPERATOR.lower():
                log.debug("Clause operator is %s, evaluate on segment",
                          operator)
                return self._check_target_in_segment(clause.values, target)
            log.debug("Attribute type %s is none return false", type)
            return False
        log.debug("evaluate clause with object %s operator %s and value %s",
                  type, operator.upper(), clause.values)
        if operator == IN_OPERATOR.lower():
            return type.in_list(clause.values)
        if operator == EQUAL_OPERATOR.lower():
            return type.equal(clause.values)
        if operator == GT_OPERATOR.lower():
            return type.greater_than(clause.values)
        if operator == STARTS_WITH_OPERATOR.lower():
            return type.starts_with(clause.values)
        if operator == ENDS_WITH_OPERATOR.lower():
            return type.ends_with(clause.values)
        if operator == CONTAINS_OPERATOR.lower():
            return type.contains(clause.values)
        if operator == EQUAL_SENSITIVE_OPERATOR.lower():
            return type.equal_sensitive(clause.values)
        # unknown operation
        return False

    def _evaluate_clauses(self, clauses: Union[Unset, Clauses],
                          target: Target) -> bool:
        if not isinstance(clauses, Unset):
            for clause in clauses:
                if self._evaluate_clause(clause, target):
                    log.debug("Successful evaluation of clause %s", clause)
                    return True
        log.debug("All clauses %s evaluated", clauses)
        return False

    def _evaluate_clauses_v2(self, clauses: Union[Unset, Clauses],
                             target: Target) -> bool:
        if not clauses or isinstance(clauses, Unset):
            return False

        for clause in clauses:
            if not self._evaluate_clause(clause, target):
                # first false clause, short-circuit and exit with false
                return False
        # all clauses have passed
        return True

    def _evaluate_rule(self, rule: ServingRule, target: Target) -> bool:
        return self._evaluate_clauses(rule.clauses, target)

    def _evaluate_rules(self, rules: ServingRules,
                        target: Target) -> Optional[str]:
        if not rules or not target:
            log.debug("There is no target or serving rule, %s, %s",
                      rules, target)
            return None

        def sort_by_priority(item: ServingRule):
            return item.priority

        log.debug("Sorting serving rules %s", rules)
        rules.sort(key=sort_by_priority)
        log.debug("Sorted serving rules %s", rules)

        identifier = None
        for rule in rules:
            # if evaluation is false just continue to next rule
            if not self._evaluate_rule(rule, target):
                log.debug(
                    "Unsuccessful evaluation of rule %s continue to next rule",
                    rule)
                continue

            # rule matched, check if there is distribution
            distribution = rule.serve.distribution
            if not isinstance(distribution, Unset) and distribution:
                log.debug("Evaluate distribution %s", distribution)
                identifier = self._evaluate_distribution(
                    distribution, target)

            # rule matched, here must be variation if distribution is None
            variation = rule.serve.variation
            if not isinstance(variation, Unset) and variation:
                log.debug("Return rule variation identifier %s", identifier)
                identifier = variation

            return identifier

        log.debug("All rules failed, return empty variation identifier")
        return None

    def _evaluate_variation_map(self, var_target_map: List[VariationMap],
                                target: Target) -> Optional[str]:
        if not target or not var_target_map:
            log.debug("Target is none")
            return None

        for variation_map in var_target_map:
            if not isinstance(variation_map.targets, Unset) and next(
                    (val for val in variation_map.targets
                     if not isinstance(val, Unset) and val.identifier ==
                        target.identifier), None) is not None:
                log.debug("Evaluate variation map with result %s",
                          variation_map.variation)
                return variation_map.variation

            segment_identifiers = variation_map.target_segments
            if not isinstance(segment_identifiers, Unset) and \
                    self._check_target_in_segment(segment_identifiers, target):
                log.debug("Evaluate variationMap with segment " +
                          "identifiers % s and return % s",
                          segment_identifiers, variation_map.variation)
                return variation_map.variation

        return None

    def _evaluate_flag(self, fc: FeatureConfig,
                       target: Target) -> Variation:
        variation: Optional[str] = fc.off_variation
        log.debug("feature %s state is %s", fc.feature, fc.state)
        if fc.state == FeatureState.ON:
            variation = None
            if not isinstance(fc.variation_to_target_map, Unset):
                variation = self._evaluate_variation_map(
                    fc.variation_to_target_map, target)
                log.debug("variation %s found in target map", variation)

            if not variation:
                variation = self._evaluate_rules(fc.rules, target)
                log.debug("variation %s found in rules", variation)

            if not variation and not isinstance(fc.default_serve.distribution,
                                                Unset):
                variation = self._evaluate_distribution(
                    fc.default_serve.distribution, target)
                log.debug(
                    "variation %s found in default serve distribution",
                    variation)

            if not variation and not isinstance(fc.default_serve.variation,
                                                Unset):
                variation = fc.default_serve.variation
                log.debug("variation %s found in default serve", variation)

        return self._find_variation(fc.variations, variation)

    def _check_prerequisite(self, parent: FeatureConfig,
                            target: Target) -> bool:
        if not isinstance(parent.prerequisites, Unset):
            log.debug('Checking pre requisites %s of parent feature %s',
                      parent.prerequisites, parent.feature)
            for pqs in parent.prerequisites:
                config = self.provider.get_flag(pqs.feature)
                if not config:
                    log.warning(
                        'Could not retrieve the pre requisite details of ' +
                        'feature flag: %s',
                        parent.feature)
                    return True

                # Pre requisite variation value evaluated below
                variation = self._evaluate_flag(config, target)
                log.debug('Pre requisite flag %s has variation %s ' +
                          'for target %s',
                          config.feature, variation, target)

                # Compare if the pre requisite variation is a possible
                # valid value of the pre requisite FF
                log.debug(
                    'Pre requisite flag %s should have the variations %s',
                    config.feature, pqs.variations)

                if isinstance(variation, Unset) or variation.identifier \
                        not in pqs.variations:
                    return False
                # Check for any nested prerequisites
                if not self._check_prerequisite(config, target):
                    return False
        return True

    def evaluate(self, identifier: str, target: Target,
                 kind: str) -> Variation:
        fc = self.provider.get_flag(identifier)
        if not fc:
            return Variation(identifier="", value=None)

        if fc.kind != kind:
            raise FlagKindMismatchException(
                f"Requested {kind} variation on {fc.kind} flag")

        if fc.prerequisites:
            prereq = self._check_prerequisite(fc, target)
            if not prereq:
                return self._find_variation(fc.variations, fc.off_variation)

        return self._evaluate_flag(fc, target)
