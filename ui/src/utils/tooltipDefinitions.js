/**
 * Tooltip definitions for UI elements
 */
export const tooltipDefinitions = {
  taskDescription: "A clear description of the task you want the prompt to accomplish. This helps the model understand the context and purpose of the prompt.",

  baseInstruction: "Your initial prompt that needs optimization. This is the starting point that will be refined through the optimization process.",

  answerFormat: "The desired format for the model's response (e.g., JSON, bullet points, paragraph, etc.). Specifying this helps ensure consistent outputs.",

  dataset: {
    label: "The dataset used for optimization. Select from predefined datasets or use your own custom data.",
    options: {
      Custom: "Use your own custom data. You'll need to provide examples in the format specified by the task.",
      GSM8k: "Grade School Math 8K - A dataset of 8,500 high quality grade school math problems. Use case: Mathematical problem solving with step-by-step reasoning.",
      SVAMP: "Simple Variations on Arithmetic Math word Problems - A dataset focused on elementary math word problems. Use case: Basic arithmetic reasoning and problem solving.",
      AQUARAT: "AQuA-RAT - A dataset of algebraic word problems with rationales. Use case: Advanced mathematical reasoning with explanations.",
      BBII: "Big Bench Instruction Induction - A dataset for testing instruction following capabilities. Use case: General instruction following and task completion."
    }
  },

  model: {
    label: "The language model to use for optimization.",
    options: {
      Gemini: "Google's Gemini model, optimized for multimodal tasks and reasoning.",
      "GPT-4": "OpenAI's GPT-4 model, known for strong instruction following and reasoning capabilities.",
      Custom: "Use a custom model by providing its API endpoint and parameters."
    }
  },

  apiKey: "Your API key for the selected model. This is required to make API calls to the model provider.",

  mutationRounds: "The number of rounds of mutation to be performed when generating different styles. Higher values may lead to better results but take longer to process.",

  refineSteps: "The number of refinement steps after each mutation round. More steps can lead to more polished prompts.",

  mutateRefineIterations: "Number of iterations for conducting mutation rounds followed by refinement of instructions. Higher values lead to more thorough optimization.",

  refineTaskEgIterations: "Number of iterations for refining task description and in-context examples for few-shot learning. Higher values improve example quality.",

  refineInstruction: "Whether to refine instructions after mutation. Enabling this leads to more polished prompts but increases processing time.",

  minCorrectCount: "Number of batches of questions to correctly answer for a prompt to be considered as performing well. Higher values ensure better quality.",

  maxEvalBatches: "Maximum number of mini-batches on which to evaluate the prompt. Higher values provide more thorough evaluation but increase processing time.",

  topN: "Number of top best-performing prompts to be considered for next iterations. Higher values explore more variations but may slow down convergence.",

  questionsBatchSize: "Number of questions to be asked to the LLM in a single batch during training. Higher values speed up training but may reduce quality.",

  useExamples: "Whether to use in-context examples during optimization. Examples help the model understand the task better and can improve results.",

  generateSyntheticExamples: "Generate synthetic examples for training when no training data is available. The model will create examples based on the task description. A dataset can still be used for evaluation.",

  generateExpertIdentity: "Generate a description of an expert who can solve the task. This helps the model adopt the right persona and approach.",

  generateIntentKeywords: "Generate keywords that describe the intent of the task. This helps the model understand the purpose of the prompt.",

  styleVariation: "Number of variations of prompts to generate in each iteration. Higher values explore more diverse approaches.",

  fewShotCount: "Number of examples to include in the prompt for few-shot learning. More examples can improve performance but increase token usage.",

  evaluationCriteria: {
    label: "Basic criteria used to evaluate and improve the prompt.",
    options: {
      Accuracy: "How well the prompt produces factually correct and precise responses.",
      Clarity: "How clear and unambiguous the prompt is.",
      Completeness: "How well the prompt covers all aspects of the task.",
      Relevance: "How relevant the prompt is to the specific task.",
      Conciseness: "How efficiently the prompt communicates without unnecessary verbosity."
    }
  },

  advancedEvaluationMetrics: {
    label: "Advanced metrics for more comprehensive prompt evaluation.",
    options: {
      Faithfulness: "Measures how faithful the generated content is to the source material.",
      SemanticSimilarity: "Evaluates semantic similarity between generated and reference outputs.",
      ContextRelevancy: "Assesses how relevant the context is to the query.",
      HitRate: "Percentage of relevant items retrieved from the total number of relevant items.",
      MRR: "Mean Reciprocal Rank - evaluates the position of the first relevant item in the results.",
      NDCG: "Normalized Discounted Cumulative Gain - measures ranking quality with position-based weighting."
    }
  },

  showDatasetPreview: "Preview and visualize the dataset before optimization to ensure it meets your requirements.",

  enableMultimodal: "Enable support for multimodal inputs like images. This allows optimizing prompts for image-based tasks.",

  saveSession: "Save the current optimization session for later use. This allows you to continue optimization or compare results.",

  sessionName: "Name for the saved optimization session. Use a descriptive name to easily identify it later."
};
