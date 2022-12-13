from typing import List, Optional, Union

import mmh3

from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.clause import Clause, Clauses
from featureflags.evaluations.constants import (CONTAINS_OPERATOR,
                                                ENDS_WITH_OPERATOR,
                                                EQUAL_OPERATOR,
                                                EQUAL_SENSITIVE_OPERATOR,
                                                GT_OPERATOR, IN_OPERATOR,
                                                ONE_HUNDRED,
                                                SEGMENT_MATCH_OPERATOR,
                                                STARTS_WITH_OPERATOR)
from featureflags.evaluations.distribution import Distribution
from featureflags.evaluations.enum import FeatureState
from featureflags.evaluations.feature import FeatureConfig
from featureflags.evaluations.serving_rule import ServingRule, ServingRules
from featureflags.evaluations.variation import Variation
from featureflags.evaluations.variation_map import VariationMap
from featureflags.models.unset import Unset
from featureflags.repository import QueryInterface
from featureflags.util import log

EMPTY_VARIATION = Variation(identifier="", value=None)


class Evaluator(object):

    def __init__(self, provider: QueryInterface):
        self.provider = provider

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
        hash = int(mmh3.hash(value))
        normalized_number = (hash % ONE_HUNDRED) + 1
        log.debug("normalized number for %s = %d", value, normalized_number)
        return normalized_number

    def _is_enabled(self, target: Target, bucket_by: str,
                    percentage: int) -> bool:
        attr_value = target.get_attr_value(bucket_by)
        if not attr_value:
            log.debug("Returns False. %s is set to %s", bucket_by, attr_value)
            return False
        bucket_id = self._get_normalized_number(bucket_by, attr_value)
        log.debug("Bucket id %d for target %s", bucket_id, target.identifier)
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
                log.info("target %s, segment %s",
                         target.identifier, segment.included)
                if not isinstance(segment.included, Unset) and \
                        next(
                            (val for val in segment.included
                             if val.identifier == target.identifier),
                            None) is not None:
                    log.debug('Target %s included in segment %s' +
                              ' via include list\n',
                              target.name, segment.name)
                    return True

                # Should Target be included via segment rules
                if segment.rules and self._evaluate_clauses(segment.rules,
                                                            target):
                    log.debug('Target %s included in segment %s via rules\n',
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
                  object, operator, clause.values)
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
            log.info('Checking pre requisites %s of parent feature %s',
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
                log.info('Pre requisite flag %s has variation %s ' +
                         'for target %s',
                         config.feature, variation, target)

                # Compare if the pre requisite variation is a possible
                # valid value of the pre requisite FF
                log.info('Pre requisite flag %s should have the variations %s',
                         config.feature, pqs.variations)

                if isinstance(variation, Unset) or variation.identifier \
                        not in pqs.variations:
                    return False
                else:
                    return self._check_prerequisite(config, target)
        return True

    def evaluate(self, identifier: str, target: Target) -> Variation:
        fc = self.provider.get_flag(identifier)
        if not fc:
            return Variation(identifier="", value=None)

        if fc.prerequisites:
            prereq = self._check_prerequisite(fc, target)
            if not prereq:
                return self._find_variation(fc.variations, fc.off_variation)

        return self._evaluate_flag(fc, target)
