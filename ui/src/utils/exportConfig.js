/**
 * Exports the form data as a YAML configuration file
 * @param {Object} formData - The form data to export
 */
export const exportConfigAsYaml = (formData) => {
  // Convert form data to YAML format
  const yaml = `prompt_technique_name: "critique_n_refine"
unique_model_id: "${formData.model === 'Gemini' ? 'gemini-2.0-flash' : formData.model === 'GPT-4' ? 'gpt-4' : 'custom-model'}"
mutate_refine_iterations: ${formData.mutationRounds}
mutation_rounds: ${formData.mutationRounds}
refine_instruction: true
refine_task_eg_iterations: ${formData.refineSteps}
top_n: 3
min_correct_count: 2
max_eval_batches: 5

# Task Description
task_description: "${formData.taskDescription}"

# Initial base instruction
base_instruction: |
  ${formData.baseInstruction.replace(/\n/g, '\n  ')}

# Answer format specification
answer_format: "${formData.answerFormat}"

# Evaluation criteria
evaluation_criteria:
${formData.evaluationCriteria.map(criteria => `  - "${criteria}"`).join('\n')}

# Optional features
use_examples: ${formData.useExamples}
generate_synthetic_examples: ${formData.useExamples}
run_without_train_examples: ${!formData.useExamples}
generate_expert_identity: true
generate_intent_keywords: true
`;

  // Create a blob with the YAML content
  const blob = new Blob([yaml], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  
  // Create a temporary link and trigger download
  const a = document.createElement('a');
  a.href = url;
  a.download = 'promptopt_config.yaml';
  document.body.appendChild(a);
  a.click();
  
  // Clean up
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
