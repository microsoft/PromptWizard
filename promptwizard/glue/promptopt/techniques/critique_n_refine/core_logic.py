import random
import re
from os.path import join
from tqdm import tqdm
from typing import Any, Dict, List
import json

from ....paramlogger import ParamLogger
from ....paramlogger.constants import LogLiterals
from ....common.base_classes import SetupConfig, UniversalBaseClass
from ....common.llm.llm_mgr import LLMMgr
from ....common.constants.log_strings import CommonLogsStr
from ...constants import PromptOptimizationParams, SupportedPromptOpt
from ...techniques.common_logic import DatasetSpecificProcessing, PromptOptimizer
from ...techniques.critique_n_refine.base_classes import CritiqueNRefinePromptPool


def extract_between(start, end, text):
    """
    Extracts the substring from 'text' that is between 'start' and 'end' strings.
    
    Parameters:
    - start (str): The starting delimiter string.
    - end (str): The ending delimiter string.
    - text (str): The text to search within.
    
    Returns:
    - str: The extracted substring between the start and end delimiters.
    """
    start_index = text.find(start)
    if start_index == -1:
        return '' 
    
    start_index += len(start)
    
    end_index = text.find(end, start_index)
    if end_index == -1:
        return ''  
    return text[start_index:end_index]


class CritiqueNRefine(PromptOptimizer, UniversalBaseClass):
    """
    TODO: Explain this method
    """

    TECHNIQUE_NAME = SupportedPromptOpt.CRITIQUE_N_REFINE.value

    class GetPromptScoreIndex:
        """
        Class to hold constants. Output of get_prompt_score() method is a list.
        This class stores mapping between output entity and its index in output of get_prompt_score() method.
        """
        PROMPT_STR = 0
        SCORE = 1
        DATASET = 2

    # This has to defined outside of constructor, so that it can be used as decorator.
    iolog = ParamLogger()

    def __init__(self, dataset: List, base_path: str, setup_config: SetupConfig,
                 prompt_pool: CritiqueNRefinePromptPool, data_processor: DatasetSpecificProcessing, logger):
        self.dataset = dataset
        self.setup_config = setup_config
        self.data_processor = data_processor
        self.logger = logger
        self.prompt_pool = prompt_pool
        base_path = join(base_path, LogLiterals.DIR_NAME)
        self.iolog.reset_eval_glue(base_path)

    @iolog.log_io_params
    def chat_completion(self, user_prompt: str, system_prompt: str = None):
        """
        Make a chat completion request to the OpenAI API.

        :param user_prompt: Text spoken by user in a conversation.
        :param system_prompt: Text spoken by system in a conversation.
        :return: Output of LLM
        """
        if not system_prompt:
            system_prompt = self.prompt_pool.system_prompt

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = LLMMgr.chat_completion(messages)
        return response

    @iolog.log_io_params
    def gen_different_styles(self, base_instruction: str, task_description: str,
                             mutation_rounds: int = 2, thinking_styles_count: int = 10) -> List:
        """
        Generate different variations of base_instruction by mixing thinking styles.

        :param base_instruction: Instruction given to LLM to solve the task defined in task_description.
        :param task_description: Description of the task to be solved.
        :param mutation_rounds: Number of rounds of mutation to be performed when generating different styles.
        :param thinking_styles_count: Number of different thinking styles descriptions to be taken from the pool of
                                      thinking styles and given to LLM as reference (in context).

        :return: List of prompts generated in `mutation_rounds` rounds of mutation.
        """
        candidate_prompts = [task_description + "\n" + base_instruction]

        for mutation_round in range(mutation_rounds):
            mutated_sample_prompt = self.prompt_pool.meta_sample_template.format(
                task_description=task_description,
                meta_prompts="\n".join(self.prompt_pool.thinking_styles[:thinking_styles_count]),
                num_variations=thinking_styles_count,
                prompt_instruction=base_instruction)
            generated_mutated_prompt = self.chat_completion(mutated_sample_prompt)
            # Find all matches of the pattern in the text
            matches = re.findall(DatasetSpecificProcessing.TEXT_DELIMITER_PATTERN_MUTATION, generated_mutated_prompt)
            candidate_prompts.extend(matches)

            self.logger.info(f"mutation_round={mutation_round} mutated_sample_prompt={mutated_sample_prompt}"
                             f"mutated_prompt_generation={generated_mutated_prompt}")

        return candidate_prompts

    @iolog.log_io_params
    def critique_and_refine(self, prompt: str, critique_example_set: List,
                            further_enhance: bool = False) -> str:
        """
        For the given prompt and examples, generate critique using LLM. Then using the generated critique, refine the prompt using LLM.

        :param prompt: Initial prompt
        :param critique_example_set: Set of examples to be given in context (as few shots)
        :param further_enhance: True, if the initial prompt gave number of correct answers more than expected threshold.
                                i.e. we try to further optimize already good prompt.
                                False, if the initial prompt gave number of correct answers less than expected
                                threshold. i.e. we try to improve poorly performing prompt.
        :return: refined prompt
        """
        example_string = self.data_processor.collate_to_str(critique_example_set,
                                                            self.prompt_pool.quest_reason_ans)

        if further_enhance:
            # Prompt to get critique on the prompt for which we got the examples right
            meta_critique_prompt = self.prompt_pool.meta_positive_critique_template
        else:
            # Prompt to get critique on the prompt for which we got the examples wrong
            meta_critique_prompt = self.prompt_pool.meta_critique_template

        meta_critique_prompt = meta_critique_prompt.format(instruction=prompt, examples=example_string)

        critique_text = self.chat_completion(meta_critique_prompt, self.prompt_pool.expert_profile)
        critique_refine_prompt = self.prompt_pool.critique_refine_template.format(instruction=prompt,
                                                                                  examples=example_string,
                                                                                  critique=critique_text,
                                                                                  steps_per_sample=1)

        refined_prompts = self.chat_completion(critique_refine_prompt, self.prompt_pool.expert_profile)
        
        refined_prompts = re.findall(DatasetSpecificProcessing.TEXT_DELIMITER_PATTERN, refined_prompts)
        
        if refined_prompts:
            final_refined_prompts = refined_prompts[0]
        else:
            raise ValueError("The LLM ouput is not in the expected format. Please rerun the code...")

        self.logger.info(f"Prompt to get critique:\n {meta_critique_prompt}"
                         f"critique received from LLM:\n {critique_text}"
                         f"Prompt to get Refinement after critique, from LLM:\n {critique_refine_prompt}"
                         f"Refined prompts received from LLM:\n {final_refined_prompts}")

        return final_refined_prompts

    @iolog.log_io_params
    def get_prompt_score(self, instructions: List[str], params: PromptOptimizationParams) -> List:
        """
        For each of the prompts in input, make LLM answer a set questions from dataset.
        Check if the answers are correct. Assign score to each prompt based on the number of batches of questions
        answered correctly. Once you get a prompt that gets all the questions right, you can stop the process.

        :params instructions: Prompts using which we'll try to solve the task
        :params params: Object of PromptOptimizationParams class, that has hyperparameters related to prompt
        optimization technique in context.
        :return: A tuple with (Prompt string,
                               score corresponding to that prompt,
                               set of examples over which we evaluated)
        """
        prompt_score_list = []

        for instruction in instructions:
            correct_count, count = 0, 0
            critique_example_set = []
            dataset_subset = random.sample(self.dataset, params.questions_batch_size)
            questions_pool = [example[DatasetSpecificProcessing.QUESTION_LITERAL] for example in dataset_subset]
            while not critique_example_set and \
                    correct_count < params.min_correct_count and \
                    count < params.max_eval_batches:
                count += 1
                solve_prompt = self.prompt_pool.solve_template.format(
                    questions_batch_size=params.questions_batch_size,
                    answer_format=params.answer_format,
                    instruction=instruction,
                    questions='\n'.join(questions_pool))
                
                generated_text = self.chat_completion(solve_prompt)
                critique_example_set = self.evaluate(generated_text, dataset_subset)
                if not critique_example_set:
                    # If all the questions were answered correctly, then we need to get a new set of questions to answer
                    dataset_subset = random.sample(self.dataset, params.questions_batch_size)
                    questions_pool = [example[DatasetSpecificProcessing.QUESTION_LITERAL] for example in dataset_subset]
                    correct_count += 1
                # 
                print("critique_example_set, correct_count")
                print(critique_example_set, correct_count)
            print("Loop completed")
            prompt_score_list.append([instruction, correct_count/count, dataset_subset])

        self.logger.info(f"prompt_score_list {prompt_score_list}")
        return prompt_score_list

    @iolog.log_io_params
    def refine_prompts(self, prompt_score_list: List, params: PromptOptimizationParams) -> List:
        """
        Further refine the prompts differently based on whether they got the subset of questions right or wrong.

        :param prompt_score_list: List of (prompt string, score for that prompt string,
        set of examples given in context)
        :param params: Object of class having hyperparameters for Prompt Optimization.
        :return: List of prompts, which were refined over input prompts.
        """
        refined_prompts = []
        for prompt, score, critique_example_set in prompt_score_list:
            if score >= params.min_correct_count/params.max_eval_batches:
                # if it's good enough prompt, how to mutate on that
                refined_prompts.append(self.critique_and_refine(prompt, critique_example_set, True))
            else:
                # if it's not good enough prompt, how to mutate on that
                refined_prompts.append(self.critique_and_refine(prompt, critique_example_set))

        self.logger.info(f"refined_prompts {refined_prompts}")
        return refined_prompts

    @iolog.log_io_params
    def evaluate(self, generated_text: str, dataset_subset: List) -> List:
        """
        Compare predicted answers with actual answers from the dataset.
        Return the list of questions for which the predicted answer was wrong.

        :param generated_text: Output of LLM, that has answers for a mini-batch of questions
                               (which were send in single go)
        :param dataset_subset: List of examples with question and ground truth.
        :return: List of examples that were wrongly classified.
        """
        # Find all matches of the pattern in the text
        answer_matches = re.findall(DatasetSpecificProcessing.ANSWER_DELIMITER_PATTERN, generated_text)
 
        # answer_matches = [self.chat_completion(FINAL_ANSWER_EXTRACTION_PROMPT.format(text=generated_text), "You are an AI assistant. Please follow the users requests.")]
        answer_matches = [generated_text]
        # 
        answers_len, dataset_len = len(answer_matches), len(dataset_subset)
        if answers_len != dataset_len:
            self.logger.info(f"Answers extracted from LLM output={answers_len}, Questions asked to LLM {dataset_len}")
            if answers_len > dataset_len:
                # Select last `dataset_len` number of extractions as final.
                answer_matches = answer_matches[-dataset_len:]

        wrong_examples = []
        for i in range(min(answers_len, dataset_len)):
            print("dataset_subset", dataset_subset)
            actual_answer = dataset_subset[i][DatasetSpecificProcessing.FINAL_ANSWER_LITERAL]
            question = dataset_subset[i][DatasetSpecificProcessing.QUESTION_LITERAL]
            is_correct, _ = self.data_processor.access_answer(answer_matches[i], actual_answer)
            if not is_correct:
                wrong_examples.append(dataset_subset[i])
        # 
        return wrong_examples

    @iolog.log_io_params
    def select_top_prompts(self, prompt_score_list: List, top_n: int) -> List:
        """
        Sort prompts in prompt_score_list, based on its performance. And return max, top `top_n` prompts.

        :param prompt_score_list: List of (prompt string, score for that prompt string,
        set of examples given in context)
        :param top_n: Max number of prompts from the top of the list, that we need to return
        :return: List of top `top_n` prompts.
        """
        sorted_prompts = sorted(prompt_score_list, key=lambda x: [x[self.GetPromptScoreIndex.SCORE],
                                                                  -len(x[self.GetPromptScoreIndex.PROMPT_STR])],
                                reverse=True)
        sorted_top_n_prompts = sorted_prompts[:top_n]
        self.logger.debug(f"Sorted top n prompts:  {sorted_top_n_prompts}")
        return sorted_top_n_prompts

    def extract_examples_frm_response(self, response_with_examples: str) -> List:
        """
        Extract the elements that constitute an example in dataset viz question, reasoning for answer and the answer.
        Put these elements to list and return.

        :param response_with_examples: Response of LLM which has synthetic examples.
        :return: A list of synthetic examples
        """
        #
        synthetic_examples = []
        parsed_data = re.findall(DatasetSpecificProcessing.TEXT_DELIMITER_PATTERN, response_with_examples, re.DOTALL)
        parsed_data = [s.strip() for s in parsed_data]

        for text in parsed_data:
            # Splitting text into question, reason, and answer
            if DatasetSpecificProcessing.QUESTION_KEY_IN_PROMPT in text and \
               DatasetSpecificProcessing.ANSWER_KEY_IN_PROMPT in text:
                question = text[text.find(DatasetSpecificProcessing.QUESTION_KEY_IN_PROMPT) +
                                len(DatasetSpecificProcessing.QUESTION_KEY_IN_PROMPT):
                                text.find(DatasetSpecificProcessing.ANSWER_KEY_IN_PROMPT)].strip()
                answer_with_reason = text[text.find(DatasetSpecificProcessing.ANSWER_KEY_IN_PROMPT) +
                                          len(DatasetSpecificProcessing.ANSWER_KEY_IN_PROMPT):].strip()

                if self.data_processor != None:
                    final_answer = self.data_processor.extract_final_answer(answer_with_reason)
                else:
                    final_answer = extract_between(text=answer_with_reason,start="<ANS_START>",end="<ANS_END>")


                formatted_data = {
                    DatasetSpecificProcessing.QUESTION_LITERAL: question,
                    DatasetSpecificProcessing.ANSWER_WITH_REASON_LITERAL: answer_with_reason,
                    DatasetSpecificProcessing.FINAL_ANSWER_LITERAL: final_answer
                }

                synthetic_examples.append(formatted_data)

        return synthetic_examples

    def generate_reasoning(self, task_description: str, instruction: str, question: str, answer: str) -> str:
        """
        For the given question return the reasoning that's needed to arrive at the provided answer

        :param task_description: Task description of the given task
        :param instruction: Instruction given to LLM for solving the given task
        :param question: Question from the task to be solved
        :param answer: Answer to the question
        :return: Reasoning that went through for getting answer `answer` for question `question`
        """

        prompt_template = self.prompt_pool.generate_reason_template.format(task_description=task_description,
                                                                           instruction=instruction,
                                                                           question=question,
                                                                           answer=answer)
        return self.chat_completion(user_prompt=prompt_template)

    @iolog.log_io_params
    def generate_expert_identity(self, task_description: str) -> str:
        """
        Generate sentence using LLM, describing the identity of an expert, who is apt to solve the task defined
        in task_description
        :param task_description: Task description of the given task
        :return: An expert profile, that can go in as system prompt and LLM would be asked to act as per this
        expert profile.
        """
        expert_prompt = self.prompt_pool.expert_template.format(task_description=task_description)
        return self.chat_completion(expert_prompt)

    @iolog.log_io_params
    def generate_intent_keywords(self, task_description: str, instruction: str):
        """
        For a given task description and instruction, generate keywords that describe the intent.

        :param task_description: Description of the task that has to be solved by LLM
        :param instruction: Instruction given to LLM for solving the given task
        """
        prompt_template = self.prompt_pool.intent_template.format(task_description=task_description, instruction=instruction)
        return self.chat_completion(user_prompt=prompt_template)

    @iolog.append_to_chained_log
    def generate_best_examples(self, examples: List, params: PromptOptimizationParams) -> List:
        """
        Generate best example to be give as few-shots for the given task.

        :param examples: List of examples. Each example is a dictionary with keys as question/reason/answer
        :param params: Object having hyperparameters for this prompt optimization technique.
        :return: List of synthetic examples
        """
        example_string = self.data_processor.collate_to_str(examples, self.prompt_pool.quest_reason_ans)
        few_shot_critique_prompt = self.prompt_pool.examples_critique_template.\
            format(prompt=params.base_instruction,
                   examples=example_string,
                   task_description=params.task_description,
                   num_examples=params.few_shot_count)
        
        critique = self.chat_completion(few_shot_critique_prompt, self.prompt_pool.expert_profile)

        gt_eg = random.sample(self.dataset, 1)
        gt_eg_string = self.data_processor.collate_to_str(gt_eg, self.prompt_pool.quest_reason_ans)
        few_shot_opt_prompt = self.prompt_pool.examples_optimization_template.\
            format(prompt=params.base_instruction,
                   examples=example_string,
                   gt_example=gt_eg_string,
                   critique=critique,
                   task_description=params.task_description,
                   num_examples=params.few_shot_count)
        synthetic_examples = self.chat_completion(few_shot_opt_prompt, self.prompt_pool.expert_profile)
        synthetic_examples = self.extract_examples_frm_response(synthetic_examples)

        return synthetic_examples

    def generate_best_examples_zero_shot(self,params: PromptOptimizationParams) -> List:
        """
        Generate best example to be give as few-shots for the given task.

        :param params: Object having hyperparameters for this prompt optimization technique.
        :return: List of synthetic examples
        """
        few_shot_critique_prompt = self.prompt_pool.examples_critique_template_zero_shot.\
            format(prompt=params.base_instruction,
                   task_description=params.task_description,
                   num_examples=params.num_train_examples)
        
        critique = self.chat_completion(few_shot_critique_prompt, self.prompt_pool.expert_profile)

        few_shot_opt_prompt = self.prompt_pool.examples_optimization_template.\
            format(prompt=params.base_instruction,
                   examples="",
                   gt_example="",
                   critique=critique,
                   task_description=params.task_description,
                   num_examples=params.num_train_examples)
        synthetic_examples = self.chat_completion(few_shot_opt_prompt, self.prompt_pool.expert_profile)
        synthetic_examples = self.extract_examples_frm_response(synthetic_examples)
        return synthetic_examples

    @iolog.append_to_chained_log
    def get_best_instr_by_critique(self, examples: List, params: PromptOptimizationParams):

        if self.data_processor != None:
            example_string = self.data_processor.collate_to_str(examples,
                                                            self.prompt_pool.quest_reason_ans)
        else:
            example_string = ""
            for example in examples:
                answer = example[DatasetSpecificProcessing.FINAL_ANSWER_LITERAL]
                if DatasetSpecificProcessing.ANSWER_WITH_REASON_LITERAL in example:
                    answer = example[DatasetSpecificProcessing.ANSWER_WITH_REASON_LITERAL]

                example_string += self.prompt_pool.quest_reason_ans.format(question=example[DatasetSpecificProcessing.QUESTION_LITERAL],
                                                        answer=answer)
            
        meta_critique_prompt = self.prompt_pool.meta_critique_template.format(instruction=params.base_instruction,
                                                                              examples=example_string)
        critique_text = self.chat_completion(meta_critique_prompt, self.prompt_pool.expert_profile)
        critique_refine_prompt = self.prompt_pool.critique_refine_template.format(instruction=params.base_instruction,
                                                                                  examples=example_string,
                                                                                  critique=critique_text,
                                                                                  steps_per_sample=1)
        refined_prompts = self.chat_completion(critique_refine_prompt)

        if self.data_processor != None:
            refined_instructions = re.findall(self.data_processor.TEXT_DELIMITER_PATTERN, refined_prompts)
        else:
            refined_instructions = re.findall(DatasetSpecificProcessing.TEXT_DELIMITER_PATTERN, refined_prompts)

        return refined_instructions[0] if refined_instructions else None

    def get_best_prompt(self, params: PromptOptimizationParams,use_examples=False,run_without_train_examples=False,generate_synthetic_examples=False) -> (str, Any):
        """
        Perform `params.max_iterations` iterations for optimizing your prompt. And return the best prompt found so far.

        :params: Object of class PromptOptimizationParams, that has all hyper-parameters needed for prompt optimization.
        :return: Best prompt for the given task and dataset.
        """

        current_base_instruction = params.base_instruction

        if not generate_synthetic_examples:
            print("\nMutating Task Description....")
            # Mutate and refine task description
            for round_num in tqdm(range(1, params.mutate_refine_iterations+1), desc="Iterations completed: "):
                self.logger.info(f"{CommonLogsStr.LOG_SEPERATOR} + Starting iteration: {round_num} \n "
                                f"current_base_instruction: {current_base_instruction}")
                candidate_prompts = self.gen_different_styles(current_base_instruction,
                                                            params.task_description,
                                                            params.mutation_rounds+1,
                                                            params.style_variation)
                
                if run_without_train_examples:
                    prompt_index = 1
                    print("\nOptimization Finished...")
                    print("\nPossible prompt variations:")
                    for candidate in candidate_prompts[:params.mutation_rounds]:
                        final_best_prompt = self.prompt_pool.final_prompt.format(
                        instruction=candidate,
                        answer_format=params.answer_format,
                        few_shot_examples="")
                        expert_identity = self.prompt_pool.system_prompt
                        if params.generate_expert_identity:
                            expert_identity = self.generate_expert_identity(params.task_description)

                        #if params.generate_intent_keywords:
                        intent_keywords = self.generate_intent_keywords(params.task_description,
                                                                            params.base_instruction)

                        final_best_prompt += "Keywords: " + intent_keywords
                        print("_______________________________________________________________________")
                        print("\nVariations "+str(prompt_index)+":\nExpert Profile:\n"+expert_identity+":\nPrompt:\n"+final_best_prompt)
                        prompt_index += 1
                    return "",""
                prompt_score_list = self.get_prompt_score(candidate_prompts, params)
                prompt_score_list = self.select_top_prompts(prompt_score_list, params.top_n)

                if params.refine_instruction:
                    refined_prompts = self.refine_prompts(prompt_score_list, params)
                    refined_prompt_score_list = self.get_prompt_score(refined_prompts, params)
                    prompt_score_list = self.select_top_prompts(refined_prompt_score_list + prompt_score_list,
                                                                params.top_n)

                current_base_instruction = prompt_score_list[0][self.GetPromptScoreIndex.PROMPT_STR]
                self.iolog.append_dict_to_chained_logs({"round_num": round_num,
                                                        "best_prompt": current_base_instruction,
                                                        "score": prompt_score_list[0][self.GetPromptScoreIndex.SCORE]
                                                        })

            examples = []

            params.base_instruction = current_base_instruction
            for example in self.dataset:
                solve_prompt = self.prompt_pool.solve_template.format(
                    questions_batch_size=1,
                    instruction=params.base_instruction,
                    answer_format=params.answer_format,
                    questions=example[DatasetSpecificProcessing.QUESTION_LITERAL])
                generated_text = self.chat_completion(solve_prompt)

                examples.extend(self.evaluate(generated_text, [example]))
                if len(examples) >= params.few_shot_count:
                    break

            if len(examples) < params.few_shot_count:
                examples += random.sample(self.dataset, params.few_shot_count - len(examples))

            # Refine task description and examples iteratively
            print("\nRefining Task description and Examples iteratively....")
            for i in tqdm(range(params.refine_task_eg_iterations)):
                refine_task_desc = random.choice([True, False])
                if refine_task_desc:
                    refined_instruction = self.get_best_instr_by_critique(examples, params)
                    if refined_instruction:
                        params.base_instruction = refined_instruction
                # comment this to turn off synthetic examples
                elif use_examples:
                        examples = self.generate_best_examples(examples, params)
        else:
            print("Generating Sythetic Examples....")
            train_examples = self.generate_best_examples_zero_shot(params)
            with open("train_synthetic.jsonl", 'w') as file:
                for record in train_examples:
                    json.dump(record, file)
                    file.write('\n')

            print("Synthetic examples saved at train.jsonl....")
            return "",""
    

        if params.generate_reasoning:
            print("\nGenerating CoT Reasoning for In-Context Examples....")
            for example in tqdm(examples):
                reason = self.generate_reasoning(params.task_description,
                                                 params.base_instruction,
                                                 example[DatasetSpecificProcessing.QUESTION_LITERAL],
                                                 example[DatasetSpecificProcessing.FINAL_ANSWER_LITERAL])

                example[DatasetSpecificProcessing.ANSWER_WITH_REASON_LITERAL] = f"{reason} " + \
                                                                                f"{DatasetSpecificProcessing.ANSWER_START}" + \
                                                                                f"{example[DatasetSpecificProcessing.FINAL_ANSWER_LITERAL]}" + \
                                                                                f"{DatasetSpecificProcessing.ANSWER_END}"
        if self.data_processor != None:
            example_string = self.data_processor.collate_to_str(examples, self.prompt_pool.quest_reason_ans)
        else:
            example_string = ""
            for example in examples:
                answer = example[DatasetSpecificProcessing.FINAL_ANSWER_LITERAL]
                if DatasetSpecificProcessing.ANSWER_WITH_REASON_LITERAL in example:
                    answer = example[DatasetSpecificProcessing.ANSWER_WITH_REASON_LITERAL]

                example_string += self.prompt_pool.quest_reason_ans.format(question=example[DatasetSpecificProcessing.QUESTION_LITERAL],
                                                            answer=answer)

        if params.few_shot_count == 0:
            final_best_prompt = self.prompt_pool.final_prompt.format(
            instruction=params.base_instruction,
            answer_format=params.answer_format,
            few_shot_examples="")
        else:
            final_best_prompt = self.prompt_pool.final_prompt.format(
                instruction=params.base_instruction,
                answer_format=params.answer_format,
                few_shot_examples=example_string)

        expert_identity = self.prompt_pool.system_prompt
        if params.generate_expert_identity:
            print("\nGenerating Expert Identity....")
            expert_identity = self.generate_expert_identity(params.task_description)
            self.logger.info(f"Expert Identity: {expert_identity}")

        if params.generate_intent_keywords:
            print("\nGenerating Intent Keywords....")
            intent_keywords = self.generate_intent_keywords(params.task_description,
                                                            params.base_instruction)

            final_best_prompt += "Keywords: " + intent_keywords
    
        self.iolog.dump_chained_log_to_file("best_prompt")
        self.logger.info(f"Final best prompt: {final_best_prompt}")

        return final_best_prompt, expert_identity
