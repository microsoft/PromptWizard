# PromptWizard API 🚀

Backend API for the PromptWizard UI.

<p align="center">
  <img src="../images/api_architecture.png" alt="API Architecture" width="700">
  <br>
  <em>PromptWizard API architecture and components</em>
</p>

## Overview

This API provides endpoints for optimizing prompts using the PromptWizard framework. It's built with Flask and designed to work with the PromptWizard UI frontend.

<p align="center">
  <img src="../images/api_sequence_diagram.png" alt="API Sequence Diagram" width="750">
  <br>
  <em>Sequence diagram showing the interaction between UI, API, and LLM services</em>
</p>

## API Endpoints

<p align="center">
  <img src="../images/api_endpoints.png" alt="API Endpoints" width="600">
  <br>
  <em>Overview of PromptWizard API endpoints and their functions</em>
</p>

### `POST /api/optimize_prompt`

Optimizes a prompt based on the provided parameters.

<p align="center">
  <img src="../images/optimize_prompt_flow.png" alt="Optimize Prompt Flow" width="650">
  <br>
  <em>The prompt optimization process flow in the API</em>
</p>

**Request Body:**

```json
{
  "taskDescription": "String - Description of the task",
  "baseInstruction": "String - Initial prompt to optimize",
  "answerFormat": "String - Desired output format",
  "model": "String - Model to use (Gemini, GPT-4, etc.)",
  "mutationRounds": "Number - Number of mutation rounds",
  "refineSteps": "Number - Number of refinement steps",
  "mutateRefineIterations": "Number - Number of iterations for mutation and refinement",
  "refineTaskEgIterations": "Number - Number of iterations for refining task examples",
  "refineInstruction": "Boolean - Whether to refine instructions after mutation",
  "minCorrectCount": "Number - Minimum number of correct answers required",
  "maxEvalBatches": "Number - Maximum number of evaluation batches",
  "topN": "Number - Number of top prompts to consider",
  "questionsBatchSize": "Number - Batch size for questions during training",
  "useExamples": "Boolean - Whether to use in-context examples",
  "generateSyntheticExamples": "Boolean - Whether to generate synthetic examples",
  "generateExpertIdentity": "Boolean - Whether to generate expert identity",
  "generateIntentKeywords": "Boolean - Whether to generate intent keywords",
  "styleVariation": "Number - Number of style variations to generate",
  "fewShotCount": "Number - Number of few-shot examples to include",
  "dataset": "String - Dataset to use (GSM8k, SVAMP, etc.)",
  "evaluationCriteria": "Array - Basic criteria for evaluation",
  "advancedEvaluationMetrics": "Array - Advanced metrics for evaluation",
  "enableMultimodal": "Boolean - Whether to enable multimodal support",
  "saveSession": "Boolean - Whether to save the optimization session",
  "sessionName": "String - Name for the saved session",
  "apiKey": "String - API key for the selected model"
}
```

**Response:**

```json
{
  "success": true,
  "optimizedPrompt": "String - The optimized prompt"
}
```

## Getting Started

### Prerequisites

- Python 3.8+
- API keys for LLMs (Gemini, OpenAI, etc.)

### Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```
     GOOGLE_API_KEY=your_gemini_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

### Running the API

```
python app.py
```

The API will be available at `http://localhost:5000`.

## Deployment

The API is configured for deployment on Vercel using the Vercel Python runtime.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server-side error

## Security Considerations

- API keys are stored in environment variables
- CORS is enabled for the frontend
- Input validation is performed on all requests
