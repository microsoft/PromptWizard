// AdvancedEvaluationMetrics.js
import React from 'react';
import Tooltip from './Tooltip';

/**
 * Advanced Evaluation Metrics component
 * @param {Object} props - Component props
 * @param {Object} props.formData - Form data state
 * @param {Function} props.handleAdvancedMetricsChange - Function to handle metrics changes
 * @param {Object} props.tooltipDefinitions - Tooltip definitions
 * @returns {JSX.Element} Advanced Evaluation Metrics component
 */
const AdvancedEvaluationMetrics = ({ formData, handleAdvancedMetricsChange, tooltipDefinitions }) => {
  const metrics = [
    'Faithfulness',
    'SemanticSimilarity',
    'ContextRelevancy',
    'HitRate',
    'MRR',
    'NDCG'
  ];

  return (
    <div className="border border-gray-200 rounded p-4 bg-gray-50 mb-6">
      <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
        <Tooltip text={tooltipDefinitions.advancedEvaluationMetrics.label}>
          Advanced Evaluation Metrics:
        </Tooltip>
      </label>
      <div className="flex flex-wrap">
        {metrics.map(metric => (
          <label key={metric} className="inline-flex items-center mr-6 mb-2">
            <input
              type="checkbox"
              value={metric}
              checked={formData.advancedEvaluationMetrics.includes(metric)}
              onChange={handleAdvancedMetricsChange}
              className="mr-2"
            />
            <Tooltip text={tooltipDefinitions.advancedEvaluationMetrics.options[metric]}>
              <span className="text-gray-700">{metric}</span>
            </Tooltip>
          </label>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-2">
        These advanced metrics provide more comprehensive evaluation of your prompts beyond basic criteria.
      </p>
    </div>
  );
};

export default AdvancedEvaluationMetrics;
