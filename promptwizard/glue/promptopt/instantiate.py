from os.path import dirname, join
import pickle
import time
from typing import Any, Tuple

from ..common.base_classes import SetupConfig
from ..common.constants.log_strings import CommonLogsStr
from ..common.utils.logging import get_glue_logger, set_logging_config
from ..common.utils.file import read_jsonl, yaml_to_class, yaml_to_dict, read_jsonl_row
from ..paramlogger import ParamLogger
from ..promptopt.constants import PromptOptimizationLiterals
from ..promptopt.techniques.common_logic import DatasetSpecificProcessing
from ..promptopt.utils import get_promptopt_class

class GluePromptOpt:
    """
    This class is trigger point for any prompt optimization method. Different prompt optimization techniques are
    represented by different classes. This class collates all the user configs present in different yaml files and
    other boilerplate code. Any of supported prompt optimization techniques can be triggered by this class.
    """
    BEST_PROMPT = None
    EXPERT_PROFILE = None
    data_processor = None
    iolog = ParamLogger()

    class EvalLiterals:
        IS_CORRECT = "is_correct"
        PREDICTED_ANS = "predicted_ans"
        LLM_OUTPUT = "llm_output"

    def __init__(self,
                 prompt_config_path: str,
                 setup_config_path: str,
                 dataset_jsonl: str,
                 data_processor: DatasetSpecificProcessing,
                 dataset_processor_pkl_path: str = None,
                 prompt_pool_path: str = None):
        """
        Collates all the configs present in different yaml files. Initialize logger, de-serialize pickle file that has
        class/method for dataset processing (for given dataset).

        :param llm_config_path: Path to yaml file that has LLM related configs.
        :param prompt_config_path: Path to yaml file that has prompt templates for the given techniques.
        :param setup_config_path: Path to yaml file that has user preferences.
        :param dataset_jsonl: Path to jsonl file that has dataset present in jsonl format.
        :param data_processor: object of DatasetSpecificProcessing class, which has data handling methods which are
        specific to that dataset
        :param dataset_processor_pkl_path: Path to pickle file that has object of class DatasetSpecificProcessing
                                           serialized.
        :param prompt_pool_path: Path to yaml file that has prompts
        """
        if dataset_jsonl != None:
            if data_processor:
                self.data_processor = data_processor
            else:
                with open(dataset_processor_pkl_path, "rb") as file:
                    self.data_processor = pickle.load(file)  # datatype: class DatasetSpecificProcessing

        prompt_config_dict = yaml_to_dict(prompt_config_path)
        prompt_opt_cls, prompt_opt_hyperparam_cls, promptpool_cls = get_promptopt_class(
            prompt_config_dict[PromptOptimizationLiterals.PROMPT_TECHNIQUE_NAME])

        self.setup_config = yaml_to_class(setup_config_path, SetupConfig)
        self.prompt_opt_param = yaml_to_class(prompt_config_path, prompt_opt_hyperparam_cls)
        current_dir = dirname(__file__)
        default_yaml_path = join(current_dir,
                                 "techniques",
                                 prompt_config_dict[PromptOptimizationLiterals.PROMPT_TECHNIQUE_NAME],
                                 "prompt_pool.yaml")

        self.prompt_pool = yaml_to_class(prompt_pool_path, promptpool_cls, default_yaml_path)

        if dataset_jsonl != None:
            dataset = read_jsonl(dataset_jsonl)
        self.prompt_opt_param.answer_format += self.prompt_pool.ans_delimiter_instruction
        base_path = join(self.setup_config.dir_info.base_dir, self.setup_config.experiment_name)
        set_logging_config(join(base_path, self.setup_config.dir_info.log_dir_name),
                           self.setup_config.mode)
        self.logger = get_glue_logger(__name__)

        if dataset_jsonl != None:
            if len(dataset) < self.prompt_opt_param.seen_set_size:
                self.prompt_opt_param.seen_set_size = len(dataset)
                self.logger.info(f"Dataset has {len(dataset)} samples. However values for seen_set_size is "
                                f"{self.prompt_opt_param.seen_set_size}. Hence resetting seen_set_size"
                                f" to {len(dataset)}")

        if self.prompt_opt_param.few_shot_count > self.prompt_opt_param.seen_set_size:
            self.prompt_opt_param.few_shot_count = self.prompt_opt_param.seen_set_size
            self.logger.info(f"Value set for few_shot_count is {self.prompt_opt_param.few_shot_count}. "
                             f"However values for seen_set_size is {self.prompt_opt_param.seen_set_size}. "
                             f"Hence resetting few_shot_count to {self.prompt_opt_param.few_shot_count}")

        if dataset_jsonl != None:
            training_dataset = dataset[:self.prompt_opt_param.seen_set_size]
        else:
            training_dataset = None
        self.logger.info(f"Setup configurations parameters: {self.setup_config} \n{CommonLogsStr.LOG_SEPERATOR}")
        self.logger.info(f"Prompt Optimization parameters: {self.prompt_opt_param} \n{CommonLogsStr.LOG_SEPERATOR}")

        # This iolog is going to be used when doing complete evaluation over test-dataset
        self.iolog.reset_eval_glue(join(base_path, "evaluation"))

        self.prompt_opt = prompt_opt_cls(training_dataset, base_path, self.setup_config,
                                         self.prompt_pool, self.data_processor, self.logger)

    def get_best_prompt(self,use_examples=False,run_without_train_examples=False,generate_synthetic_examples=False) -> Tuple[str, Any]:
        """
        Call get_best_prompt() method of class PromptOptimizer & return its value.
        :return: (best_prompt, expert_profile)
            best_prompt-> Best prompt for a given task description
            expert_profile-> Description of an expert who is apt to solve the task at hand. LLM would be asked to take
            identity of described in expert_profile.
        """
        start_time = time.time()
        self.BEST_PROMPT, self.EXPERT_PROFILE = self.prompt_opt.get_best_prompt(self.prompt_opt_param,use_examples=use_examples,run_without_train_examples=run_without_train_examples,generate_synthetic_examples=generate_synthetic_examples)

        self.logger.info(f"Time taken to find best prompt: {(time.time() - start_time)} sec")
        return self.BEST_PROMPT, self.EXPERT_PROFILE

    def evaluate(self, test_dataset_jsonl: str) -> float:
        """
        Evaluate the performance of self.BEST_PROMPT over test dataset. Return the accuracy.

        :param test_dataset_jsonl: Path to jsonl file that has test dataset
        :return: Percentage accuracy
        """

        start_time = time.time()
        self.logger.info(f"Evaluation started {CommonLogsStr.LOG_SEPERATOR}")
        if not self.BEST_PROMPT:
            self.logger.error("BEST_PROMPT attribute is not set. Please set self.BEST_PROMPT attribute of this object, "
                              "either manually or by calling get_best_prompt() method.")
            return

        total_correct = 0
        total_count = 0
        for json_obj in read_jsonl_row(test_dataset_jsonl):
            answer = self.predict_and_access(json_obj[DatasetSpecificProcessing.QUESTION_LITERAL],
                                             json_obj[DatasetSpecificProcessing.FINAL_ANSWER_LITERAL])
      
            total_correct += answer[self.EvalLiterals.IS_CORRECT]
            total_count += 1
            result = {"accuracy": f"{total_correct}/{total_count} : {total_correct/total_count}%",
                      "predicted": answer[self.EvalLiterals.PREDICTED_ANS],
                      "actual": json_obj[DatasetSpecificProcessing.FINAL_ANSWER_LITERAL]}
            self.iolog.append_dict_to_chained_logs(result)
            self.logger.info(result)

        self.iolog.dump_chained_log_to_file(file_name=f"eval_result_{self.setup_config.experiment_name}")
        self.logger.info(f"Time taken for evaluation: {(time.time() - start_time)} sec")
        return total_correct / total_count

    @iolog.log_io_params
    def predict_and_access(self, question: str, gt_answer: str) -> Tuple[bool, str, str]:
        """
        For the given input question, get answer to it from LLM, using the BEST_PROMPT & EXPERT_PROFILE
        computes earlier.

        :param question: Question to be asked to LLM, to solve
        :param gt_answer: Ground truth, final answer.
        :return:  (is_correct, predicted_ans, llm_output)
                is_correct -> Tells if prediction by LLM was correct.
                predicted_ans -> is the actual predicted answer by LLM.
                llm_output -> Output text generated by LLM for the given question
        :rtype: (bool, str, str)
        """
        final_prompt = self.prompt_pool.eval_prompt.format(instruction=self.BEST_PROMPT,
                                                           question=question)
        llm_output = self.prompt_opt.chat_completion(user_prompt=final_prompt, system_prompt=self.EXPERT_PROFILE)
        
        is_correct, predicted_ans = self.data_processor.access_answer(llm_output, gt_answer)
        return {self.EvalLiterals.IS_CORRECT: is_correct,
                self.EvalLiterals.PREDICTED_ANS: predicted_ans,
                self.EvalLiterals.LLM_OUTPUT: llm_output}

