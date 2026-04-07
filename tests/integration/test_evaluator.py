import json
import os
from typing import Any, Dict, List

import pytest
from attr import define

from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.evaluator import Evaluator
from featureflags.lru_cache import LRUCache
from featureflags.openapi.config.models.feature_config import (
    FeatureConfig, FeatureConfigKind)
from featureflags.openapi.config.models.segment import Segment
from featureflags.repository import Repository

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = cwd = BASE_PATH + "/ff-test-cases/tests/"

cache = LRUCache()
repository = Repository(cache)
evaluator = Evaluator(repository)


@define
class Test:
    flag: str
    target: str
    expected: Any

    @classmethod
    def from_dict(cls, source: Dict[str, Any]) -> 'Test':
        return Test(source["flag"], source.get("target", "default"),
                    source["expected"])


@define
class Feature:
    flags: List[FeatureConfig]
    segments: List[Segment]
    targets: List[Target]
    tests: List[Test]

    @classmethod
    def from_dict(cls, source: Dict[str, Any]) -> 'Feature':
        flags = [FeatureConfig.from_dict(flag) for flag in source["flags"]]

        segments = []
        if "segments" in source:
            segments = [Segment.from_dict(segment)
                        for segment in source["segments"]]
        targets = []
        if "targets" in source:
            targets = [Target.from_dict(target) for
                       target in source["targets"]]

        tests = [Test.from_dict(test) for test in source["tests"]]

        return Feature(flags=flags, segments=segments, targets=targets,
                       tests=tests)


@define
class TestCase:
    name: str
    flag: str
    target: str
    expected: str
    targets: List[Target]


def load_json_test_file(filename: str) -> Feature:
    result = None
    with open(filename, 'r') as f:
        result = Feature.from_dict(json.load(f))
    return result


def load_test_files():
    result = []
    for r, d, f in os.walk(PATH):
        for file in f:
            if '.json' in file:
                fname = os.path.join(r, file)
                print(f'Loading File: {fname}.')
                usecase = load_json_test_file(fname)
                # usecase.flag.feature += file
                result.append((fname, usecase))
    return result


def usecase_provider():
    usecases = load_test_files()

    result = []
    for fname, usecase in usecases:
        for flag in usecase.flags:
            repository.set_flag(flag)

        for segment in usecase.segments:
            repository.set_segment(segment)

        for test_case in usecase.tests:
            result.append(
                TestCase(name='given flag {} then target {} should get {}'
                         .format(test_case.flag,
                                 test_case.target,
                                 test_case.expected),
                         flag=test_case.flag,
                         target=test_case.target,
                         expected=test_case.expected,
                         targets=usecase.targets))

    return result


def feature_name(tc):
    return tc.name


@pytest.mark.parametrize('tc', usecase_provider(), ids=feature_name)
def test_evaluator(tc: TestCase):
    target = None
    if tc.target != "_no_target":
        target = next(
            (val for val in tc.targets if val.identifier == tc.target),
            None
        )

    got = None

    switch_kind = {
        FeatureConfigKind.BOOLEAN:
            lambda: evaluator.evaluate(tc.flag, target, "boolean")
            .bool(target, tc.flag, default=False),
        FeatureConfigKind.STRING:
            lambda: evaluator.evaluate(tc.flag, target, "string").string(
                target, tc.flag,
                default="failed"),
        FeatureConfigKind.INT:
            lambda: evaluator.evaluate(tc.flag, target, "int")
            .number(target, tc.flag, default=0.100),
        FeatureConfigKind.JSON:
            lambda: evaluator.evaluate(tc.flag, target, "json")
            .json(target, tc.flag, default={}),
    }

    kind = repository.get_flag(tc.flag).kind
    got = switch_kind[kind]()

    if kind == FeatureConfigKind.JSON:
        tc.expected = json.loads(tc.expected)

    assert got == tc.expected
