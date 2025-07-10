import os
from dotenv import load_dotenv
import yaml
import google.generativeai as genai
from dataclasses import dataclass

# Load environment variables from system
load_dotenv()

@dataclass
class PromptOptimizationParams:
    task_description: str
    base_instruction: str
    answer_format: str
    max_iterations: int
    evaluation_criteria: list
    temperature: float

class PromptOptimizer:
    def __init__(self, setup_config, task_description):
        self.setup_config = setup_config
        self.task_description = task_description

        # Initialize Gemini
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-api-key":
            print("\nERROR: Valid GOOGLE_API_KEY not found in system environment variables.")
            print("Please set a valid Gemini API key in your system environment.")
            print("You can get an API key from https://ai.google.dev/")
            print("\nFor testing purposes, we'll continue with a mock optimization.")
            self.use_mock = True
        else:
            self.use_mock = False
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def optimize_prompt(self, base_prompt, criteria):
        if self.use_mock:
            # Return a mock optimized prompt for testing
            print(f"\nMock optimization iteration:")
            print(f"Base prompt: {base_prompt[:50]}...")
            print(f"Criteria: {', '.join(criteria)}")

            # Create a simple mock optimization by adding some text
            optimized = base_prompt + "\n\nAdditional instructions: Please ensure all sensitive data is properly identified and coordinates are precise to the pixel level."
            return optimized
        else:
            # Use the actual Gemini model
            chat = self.model.start_chat(history=[])

            optimization_prompt = f"""
            Task: {self.task_description}
            Base prompt: {base_prompt}
            Evaluation criteria: {', '.join(criteria)}

            Please optimize this prompt to better meet the evaluation criteria.
            Return only the optimized prompt without any explanations.
            """

            response = chat.send_message(optimization_prompt)
            return response.text

    def get_best_prompt(self, params):
        current_prompt = params.base_instruction

        print(f"\nStarting prompt optimization with {params.max_iterations} iterations")
        print(f"Task: {params.task_description}")

        for i in range(params.max_iterations):
            print(f"\nIteration {i+1}/{params.max_iterations}:")
            optimized_prompt = self.optimize_prompt(
                current_prompt,
                params.evaluation_criteria
            )
            current_prompt = optimized_prompt

        return current_prompt, None

def main():
    # Load configurations
    with open('configs/promptopt_config.yaml', 'r') as f:
        prompt_config = yaml.safe_load(f)

    with open('configs/setup_config.yaml', 'r') as f:
        setup_config = yaml.safe_load(f)

    # Extract only the needed parameters from the config
    params = PromptOptimizationParams(
        task_description=prompt_config['task_description'],
        base_instruction=prompt_config['base_instruction'],
        answer_format=prompt_config['answer_format'],
        evaluation_criteria=prompt_config['evaluation_criteria'],
        max_iterations=prompt_config.get('mutate_refine_iterations', 3),  # Default to 3 if not found
        temperature=setup_config['llm'].get('temperature', 0.0)  # Default to 0.0 if not found
    )

    # Initialize optimizer
    optimizer = PromptOptimizer(
        setup_config=setup_config,
        task_description=params.task_description
    )

    # Run optimization
    best_prompt, _ = optimizer.get_best_prompt(params=params)

    print("\nBest optimized prompt:")
    print(best_prompt)

if __name__ == "__main__":
    main()
