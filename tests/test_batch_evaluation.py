import logging
from pathlib import Path

import pytest
import yaml

from promptwizard.glue.common.base_classes import SetupConfig
from promptwizard.glue.promptopt.techniques.common_logic import (
    DatasetSpecificProcessing,
)
from promptwizard.glue.promptopt.techniques.critique_n_refine.base_classes import (
    CritiqueNRefinePromptPool,
)
from promptwizard.glue.promptopt.techniques.critique_n_refine.core_logic import (
    CritiqueNRefine,
    extract_between,
)


class TaggedAnswerProcessor(DatasetSpecificProcessing):
    """Use the tag-based extraction contract documented for dataset processors."""

    def __init__(self):
        self.received_outputs = []

    def dataset_to_jsonl(self, dataset_jsonl, task, **kwargs):
        raise NotImplementedError("These tests use an in-memory dataset")

    def extract_final_answer(self, answer):
        self.received_outputs.append(answer)
        return extract_between(self.ANSWER_START, self.ANSWER_END, answer)


class LastTaggedAnswerProcessor(TaggedAnswerProcessor):
    """Also cover extractors that select the final answer after reasoning."""

    def extract_final_answer(self, answer):
        self.received_outputs.append(answer)
        return answer.rsplit(self.ANSWER_START, 1)[-1].split(self.ANSWER_END, 1)[0]


DATASET = [
    {"question": "2 + 2?", "final_answer": "4"},
    {"question": "5 + 5?", "final_answer": "10"},
    {"question": "3 + 4?", "final_answer": "7"},
]


def tagged(*answers):
    return "\n".join("<ANS_START>" + answer + "<ANS_END>" for answer in answers)


@pytest.fixture(scope="module")
def evaluation_setup(tmp_path_factory):
    repository = Path(__file__).resolve().parents[1]
    with (repository / "demos/bbh/configs/setup_config.yaml").open() as config_file:
        setup_config = SetupConfig(**yaml.safe_load(config_file))
    pool_path = (
        repository
        / "promptwizard/glue/promptopt/techniques/critique_n_refine/prompt_pool.yaml"
    )
    with pool_path.open() as pool_file:
        prompt_pool = CritiqueNRefinePromptPool(**yaml.safe_load(pool_file))
    return tmp_path_factory.mktemp("batch_evaluation"), setup_config, prompt_pool


@pytest.fixture(params=[TaggedAnswerProcessor, LastTaggedAnswerProcessor])
def optimizer(evaluation_setup, request):
    log_directory, setup_config, prompt_pool = evaluation_setup
    return CritiqueNRefine(
        DATASET,
        str(log_directory),
        setup_config,
        prompt_pool,
        request.param(),
        logging.getLogger(__name__),
    )


@pytest.mark.parametrize(
    "completion,wrong_indices",
    [
        (tagged("4", "10", "7"), []),
        (tagged("4", "10", "999"), [2]),
        (tagged("999", "10", "7"), [0]),
        (tagged("4"), [1, 2]),
        (tagged("999", "10"), [0, 2]),
        (tagged("", "10", "7"), [0]),
        (tagged("discarded", "4", "10", "7"), []),
        ("4\n10\n7", [0, 1, 2]),
        ("", [0, 1, 2]),
    ],
)
def test_evaluate_grades_each_question(optimizer, completion, wrong_indices):
    assert optimizer.evaluate(completion, DATASET) == [
        DATASET[index] for index in wrong_indices
    ]


@pytest.mark.parametrize("answer,correct", [("4", True), ("999", False)])
def test_evaluate_single_question_keeps_full_completion(optimizer, answer, correct):
    completion = "Reasoning before the answer. " + tagged(answer) + " Explanation."
    expected = [] if correct else DATASET[:1]
    assert optimizer.evaluate(completion, DATASET[:1]) == expected
    assert optimizer.data_processor.received_outputs == [completion]


def test_evaluate_empty_dataset(optimizer):
    assert optimizer.evaluate(tagged("4"), []) == []
    assert optimizer.data_processor.received_outputs == []


def test_evaluate_multiline_answers(optimizer):
    dataset = [
        {"question": "Two lines?", "final_answer": "first\nsecond"},
        DATASET[1],
    ]
    assert optimizer.evaluate(tagged("first\nsecond", "10"), dataset) == []
