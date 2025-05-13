from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yaml
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
load_dotenv()

# Configure global error handlers to ensure JSON responses
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        "success": False,
        "error": str(e) if app.debug else "Internal server error"
    }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "success": True,
        "status": "API is running",
        "version": "1.0.0"
    })

# API key validation endpoint
@app.route('/api/validate_key', methods=['POST'])
def validate_key():
    try:
        data = request.json
        api_key = data.get('apiKey', '')
        model = data.get('model', 'Gemini')

        if not api_key:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "No API key provided"
            })

        # For Gemini model
        if model == 'Gemini':
            try:
                # Try to initialize Gemini with the provided key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')

                # Try a simple generation to validate the key
                logger.info("Testing API key with a simple generation...")
                response = model.generate_content("Hello, testing API key validation.")
                logger.info(f"API key validation successful: {response.text[:30]}...")

                return jsonify({
                    "success": True,
                    "valid": True,
                    "message": "API key is valid"
                })
            except Exception as e:
                error_message = str(e)
                logger.error(f"API key validation failed: {error_message}")

                if "API key not valid" in error_message:
                    message = "Invalid API key"
                else:
                    message = f"Error validating API key: {error_message}"

                return jsonify({
                    "success": False,
                    "valid": False,
                    "message": message
                })

        # For other models (mock validation for now)
        return jsonify({
            "success": True,
            "valid": True,
            "message": f"API key validation for {model} is not implemented yet. Assuming valid."
        })

    except Exception as e:
        logger.error(f"Error in validate_key endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "valid": False,
            "message": f"Error: {str(e)}"
        }), 500

@dataclass
class PromptOptimizationParams:
    task_description: str
    base_instruction: str
    answer_format: str
    max_iterations: int
    evaluation_criteria: list
    temperature: float
    mutate_refine_iterations: int = 3
    refine_task_eg_iterations: int = 3
    refine_instruction: bool = True
    min_correct_count: int = 3
    max_eval_batches: int = 6
    top_n: int = 1
    questions_batch_size: int = 1
    generate_expert_identity: bool = True
    generate_intent_keywords: bool = False
    style_variation: int = 5
    few_shot_count: int = 5
    advanced_evaluation_metrics: list = None

class PromptOptimizer:
    def __init__(self, setup_config, task_description):
        self.setup_config = setup_config
        self.task_description = task_description

        # Initialize Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        logger.info(f"API key from environment: {'VALID' if api_key and api_key != 'your-gemini-api-key' else 'NOT VALID OR MISSING'}")

        if not api_key or api_key == "your-gemini-api-key":
            logger.warning("GOOGLE_API_KEY not found or not valid in environment variables")
            self.use_mock = True
        else:
            try:
                # Configure the API
                genai.configure(api_key=api_key)

                # Test the API with a simple request
                logger.info("Testing Gemini API connection...")
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                test_response = self.model.generate_content("Hello, testing the API connection.")
                logger.info(f"API test successful: {test_response.text[:30]}...")

                self.use_mock = False
                logger.info("Using REAL Gemini API for optimization")
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Error initializing Gemini: {str(e)}\n{error_traceback}")
                self.use_mock = True
                logger.warning("Falling back to MOCK implementation due to API initialization error")

    def optimize_prompt(self, base_prompt, criteria):
        if self.use_mock:
            # Return a mock optimized prompt for testing
            logger.info(f"Using MOCK optimization (no valid API key) for: {base_prompt[:50]}...")

            # Create a simple mock optimization by adding some text
            optimized = base_prompt + "\n\nAdditional instructions: Please ensure all responses are clear, concise, and directly address the query. Maintain a helpful and informative tone throughout."

            # Log a warning about using mock implementation
            logger.warning("USING MOCK IMPLEMENTATION: No valid API key provided. To use the actual Gemini API, please provide a valid API key in the .env file or through the UI.")
            return optimized
        else:
            # Use the actual Gemini model
            try:
                chat = self.model.start_chat(history=[])

                optimization_prompt = f"""
                Task: {self.task_description}
                Base prompt: {base_prompt}
                Evaluation criteria: {', '.join(criteria)}

                Please optimize this prompt to better meet the evaluation criteria.
                Return only the optimized prompt without any explanations.
                """

                logger.info(f"Sending optimization request to Gemini with prompt: {optimization_prompt[:100]}...")
                response = chat.send_message(optimization_prompt)
                logger.info(f"Received response from Gemini: {response.text[:100]}...")
                return response.text
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Error in optimize_prompt: {str(e)}\n{error_traceback}")
                # Fallback to mock response with error details
                return base_prompt + f"\n\n[Error occurred during optimization: {str(e)}]"

    def get_best_prompt(self, params, use_examples=False, run_without_train_examples=True, generate_synthetic_examples=False):
        current_prompt = params.base_instruction

        logger.info(f"Starting prompt optimization with {params.max_iterations} iterations")
        logger.info(f"Task: {params.task_description}")
        logger.info(f"Advanced options: generate_expert_identity={params.generate_expert_identity}, generate_intent_keywords={params.generate_intent_keywords}")
        logger.info(f"Examples options: use_examples={use_examples}, run_without_train_examples={run_without_train_examples}, generate_synthetic_examples={generate_synthetic_examples}")

        # If generate_expert_identity is enabled, add expert profile to the prompt
        if params.generate_expert_identity:
            expert_profile = self.generate_expert_profile(params.task_description)
            if not self.use_mock:
                current_prompt = f"You are an expert in {params.task_description}.\n{expert_profile}\n\n{current_prompt}"
                logger.info("Added expert profile to prompt")

        # If generate_intent_keywords is enabled, add keywords to the prompt
        if params.generate_intent_keywords:
            keywords = self.generate_keywords(params.task_description)
            if not self.use_mock:
                current_prompt = f"{current_prompt}\n\nKeywords: {keywords}"
                logger.info("Added intent keywords to prompt")

        for i in range(params.max_iterations):
            logger.info(f"Iteration {i+1}/{params.max_iterations}")
            optimized_prompt = self.optimize_prompt(
                current_prompt,
                params.evaluation_criteria
            )
            current_prompt = optimized_prompt

        # Return a tuple with the optimized prompt and None to match the expected return format
        return current_prompt, None

    def generate_expert_profile(self, task_description):
        """Generate an expert profile based on the task description"""
        if self.use_mock:
            return "Expert in the field with extensive knowledge and experience."

        try:
            prompt = f"""
            Generate a detailed expert profile for someone who is highly skilled at: {task_description}
            The profile should describe their expertise, background, and skills.
            Keep it to 2-3 sentences maximum.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating expert profile: {str(e)}")
            return "Expert in the field with extensive knowledge and experience."

    def generate_keywords(self, task_description):
        """Generate keywords based on the task description"""
        if self.use_mock:
            return "expertise, knowledge, skills, professional"

        try:
            prompt = f"""
            Generate 5-7 keywords that capture the essence of this task: {task_description}
            Return only the keywords separated by commas.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating keywords: {str(e)}")
            return "expertise, knowledge, skills, professional"

@app.route('/api/optimize_prompt', methods=['POST'])
def optimize_prompt():
    try:
        data = request.json
        logger.info(f"Received optimization request: {data}")

        # Extract parameters from request
        task_description = data.get('taskDescription', '')
        base_instruction = data.get('baseInstruction', '')
        answer_format = data.get('answerFormat', '')
        model = data.get('model', 'Gemini')
        mutation_rounds = int(data.get('mutationRounds', 3))
        refine_steps = int(data.get('refineSteps', 2))
        mutate_refine_iterations = int(data.get('mutateRefineIterations', 3))
        refine_task_eg_iterations = int(data.get('refineTaskEgIterations', 3))
        refine_instruction = data.get('refineInstruction', True)
        min_correct_count = int(data.get('minCorrectCount', 3))
        max_eval_batches = int(data.get('maxEvalBatches', 6))
        top_n = int(data.get('topN', 1))
        questions_batch_size = int(data.get('questionsBatchSize', 1))
        evaluation_criteria = data.get('evaluationCriteria', [])
        advanced_evaluation_metrics = data.get('advancedEvaluationMetrics', [])
        dataset = data.get('dataset', 'Custom')
        custom_dataset = data.get('customDataset')
        use_examples = data.get('useExamples', False)
        generate_synthetic_examples = data.get('generateSyntheticExamples', False)
        generate_expert_identity = data.get('generateExpertIdentity', True)
        generate_intent_keywords = data.get('generateIntentKeywords', False)
        style_variation = int(data.get('styleVariation', 5))
        few_shot_count = int(data.get('fewShotCount', 5))
        enable_multimodal = data.get('enableMultimodal', False)
        save_session = data.get('saveSession', False)
        session_name = data.get('sessionName', '')

        # Log dataset information
        if dataset == 'Custom' and custom_dataset:
            logger.info(f"Custom dataset provided with {len(custom_dataset)} examples")
        else:
            logger.info(f"Using predefined dataset: {dataset}")

        # If no evaluation criteria provided, use default ones
        if not evaluation_criteria:
            evaluation_criteria = ["Clarity", "Accuracy", "Completeness"]

        # Create a simple setup config
        setup_config = {
            'llm': {
                'model_type': model,
                'temperature': 0.0
            }
        }

        # Initialize parameters
        params = PromptOptimizationParams(
            task_description=task_description,
            base_instruction=base_instruction,
            answer_format=answer_format,
            max_iterations=mutation_rounds,
            evaluation_criteria=evaluation_criteria,
            temperature=0.0,
            mutate_refine_iterations=mutate_refine_iterations,
            refine_task_eg_iterations=refine_task_eg_iterations,
            refine_instruction=refine_instruction,
            min_correct_count=min_correct_count,
            max_eval_batches=max_eval_batches,
            top_n=top_n,
            questions_batch_size=questions_batch_size,
            generate_expert_identity=generate_expert_identity,
            generate_intent_keywords=generate_intent_keywords,
            style_variation=style_variation,
            few_shot_count=few_shot_count,
            advanced_evaluation_metrics=advanced_evaluation_metrics
        )

        # Get API key from request or environment
        api_key = data.get('apiKey')
        if api_key:
            # If API key is provided in the request, temporarily set it in the environment
            logger.info("Using API key from request")
            os.environ["GOOGLE_API_KEY"] = api_key
        else:
            logger.info("No API key in request, using environment variable if available")

        # Initialize optimizer
        optimizer = PromptOptimizer(
            setup_config=setup_config,
            task_description=task_description
        )

        # Add custom dataset if provided
        examples = None
        if dataset == 'Custom' and custom_dataset and use_examples:
            try:
                # Convert custom dataset to the format expected by the optimizer
                examples = []
                for item in custom_dataset:
                    if 'input' in item and 'output' in item:
                        examples.append({
                            'question': item['input'],
                            'answer': item['output']
                        })
                logger.info(f"Using {len(examples)} examples from custom dataset")
            except Exception as e:
                logger.error(f"Error processing custom dataset: {str(e)}")
                examples = None

        # Run optimization
        optimized_prompt, _ = optimizer.get_best_prompt(
            params,
            use_examples=use_examples,
            run_without_train_examples=(not use_examples),
            generate_synthetic_examples=generate_synthetic_examples
        )

        return jsonify({
            'success': True,
            'optimizedPrompt': optimized_prompt
        })

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in optimize_prompt endpoint: {str(e)}\n{error_traceback}")

        # Return a more user-friendly error message
        error_message = str(e)
        if "not found in environment variables" in error_message:
            error_message = "API key not configured. Please check your API key."

        return jsonify({
            'success': False,
            'error': error_message,
            'details': error_traceback if app.debug else None
        }), 500

if __name__ == '__main__':
    # Set up proper error handling for production
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        app.config['PROPAGATE_EXCEPTIONS'] = False
    else:
        app.config['DEBUG'] = True
        app.config['PROPAGATE_EXCEPTIONS'] = True

    # Run the app
    # Try port 5000 first, fallback to 5001 if that's in use
    try:
        app.run(debug=app.config['DEBUG'], port=5000)
    except OSError:
        print("Port 5000 is in use, trying port 5001...")
        app.run(debug=app.config['DEBUG'], port=5001)
