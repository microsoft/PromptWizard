// AdvancedOptimizationParams.js
import React from 'react';
import Tooltip from './Tooltip';

/**
 * Advanced Optimization Parameters component
 * @param {Object} props - Component props
 * @param {Object} props.formData - Form data state
 * @param {Function} props.handleChange - Function to handle form changes
 * @returns {JSX.Element} Advanced Optimization Parameters component
 */
const AdvancedOptimizationParams = ({ formData, handleChange, tooltipDefinitions }) => {
  return (
    <div className="border border-gray-200 rounded p-4 bg-gray-50 mb-6">
      <h3 className="text-lg font-semibold mb-4">Advanced Optimization Parameters</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Mutate Refine Iterations */}
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-1" htmlFor="mutateRefineIterations">
            <Tooltip text={tooltipDefinitions.mutateRefineIterations}>
              Mutate Refine Iterations:
            </Tooltip>
          </label>
          <input
            className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
            id="mutateRefineIterations"
            type="number"
            min="1"
            max="10"
            value={formData.mutateRefineIterations}
            onChange={handleChange}
          />
        </div>

        {/* Refine Task Examples Iterations */}
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-1" htmlFor="refineTaskEgIterations">
            <Tooltip text={tooltipDefinitions.refineTaskEgIterations}>
              Refine Examples Iterations:
            </Tooltip>
          </label>
          <input
            className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
            id="refineTaskEgIterations"
            type="number"
            min="1"
            max="10"
            value={formData.refineTaskEgIterations}
            onChange={handleChange}
          />
        </div>

        {/* Min Correct Count */}
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-1" htmlFor="minCorrectCount">
            <Tooltip text={tooltipDefinitions.minCorrectCount}>
              Min Correct Count:
            </Tooltip>
          </label>
          <input
            className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
            id="minCorrectCount"
            type="number"
            min="1"
            max="10"
            value={formData.minCorrectCount}
            onChange={handleChange}
          />
        </div>

        {/* Max Eval Batches */}
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-1" htmlFor="maxEvalBatches">
            <Tooltip text={tooltipDefinitions.maxEvalBatches}>
              Max Eval Batches:
            </Tooltip>
          </label>
          <input
            className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
            id="maxEvalBatches"
            type="number"
            min="1"
            max="20"
            value={formData.maxEvalBatches}
            onChange={handleChange}
          />
        </div>

        {/* Top N */}
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-1" htmlFor="topN">
            <Tooltip text={tooltipDefinitions.topN}>
              Top N Prompts:
            </Tooltip>
          </label>
          <input
            className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
            id="topN"
            type="number"
            min="1"
            max="5"
            value={formData.topN}
            onChange={handleChange}
          />
        </div>

        {/* Questions Batch Size */}
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-1" htmlFor="questionsBatchSize">
            <Tooltip text={tooltipDefinitions.questionsBatchSize}>
              Questions Batch Size:
            </Tooltip>
          </label>
          <input
            className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
            id="questionsBatchSize"
            type="number"
            min="1"
            max="10"
            value={formData.questionsBatchSize}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Refine Instruction Checkbox */}
      <div className="flex items-center mb-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            id="refineInstruction"
            checked={formData.refineInstruction}
            onChange={handleChange}
            className="mr-2"
          />
          <Tooltip text={tooltipDefinitions.refineInstruction}>
            <span className="text-gray-700">Refine Instruction After Mutation</span>
          </Tooltip>
        </label>
      </div>
    </div>
  );
};

export default AdvancedOptimizationParams;
