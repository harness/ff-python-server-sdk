
import pytest
import json
import os
from typing import Any, Dict, List
from attr import define

from featureflags.evaluations.feature import FeatureConfig, FeatureConfigKind
from featureflags.evaluations.segment import Segment
from featureflags.evaluations.auth_target import Target
from featureflags.lru_cache import LRUCache
from featureflags.repository import Repository
from featureflags.evaluations.evaluator import Evaluator


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = cwd = BASE_PATH + "/ff-test-cases/tests/"


cache = LRUCache()
repository = Repository(cache)
evaluator = Evaluator(repository)


@define
class Usecase:
    flag: FeatureConfig
    segments: List[Segment]
    targets: List[Target]
    expected: Dict[str, Any]

    @classmethod
    def from_dict(cls, source: Dict[str, Any]) -> 'Usecase':
        flag = FeatureConfig.from_dict(source["flag"])

        segments = []
        if "segments" in source:
            segments = [Segment.from_dict(segment)
                        for segment in source["segments"]]
        targets = [Target.from_dict(target) for target in source["targets"]]
        expected = source["expected"]
        return Usecase(flag=flag, segments=segments, targets=targets,
                       expected=expected)


def load_json_test_file(filename: str) -> Usecase:
    result = None
    with open(filename, 'r') as f:
        result = Usecase.from_dict(json.load(f))
    return result


def load_test_files():
    result = []
    for file in os.listdir(PATH):
        if file.endswith(".json"):
            fname = os.path.join(PATH, file)
            usecase = load_json_test_file(fname)
            usecase.flag.feature += file
            result.append((fname, usecase))
    return result


def usecase_provider():
    usecases = load_test_files()

    result = []
    for fname, usecase in usecases:
        repository.set_flag(usecase.flag)

        for segment in usecase.segments:
            repository.set_segment(segment)

        for identifier, value in usecase.expected.items():
            result.append((fname, identifier, value, usecase))

    return result


@pytest.mark.parametrize('fname,identifier,expected,usecase',
                         usecase_provider())
def test_evaluator(fname, identifier, expected, usecase):
    target = None
    if identifier != "_no_target":
        target = next(
            (val for val in usecase.targets if val.identifier == identifier),
            None
        )

    got = None

    switch_kind = {
        FeatureConfigKind.BOOLEAN:
            lambda: evaluator.evaluate(usecase.flag.feature,
                                       target,
                                       FeatureConfigKind.BOOLEAN).bool(),
        FeatureConfigKind.STRING:
            lambda: evaluator.evaluate(usecase.flag.feature,
                                       target,
                                       FeatureConfigKind.STRING).string(),
        FeatureConfigKind.INT:
            lambda: evaluator.evaluate(usecase.flag.feature,
                                       target,
                                       FeatureConfigKind.INT).int(),
        FeatureConfigKind.NUMBER:
            lambda: evaluator.evaluate(usecase.flag.feature,
                                       target,
                                       FeatureConfigKind.NUMBER).number(),
        FeatureConfigKind.JSON:
            lambda: evaluator.evaluate(usecase.flag.feature,
                                       target,
                                       FeatureConfigKind.JSON).json(),
    }

    got = switch_kind[usecase.flag.kind]()

    assert got == expected
