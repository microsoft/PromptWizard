// SessionManagement.js
import React from 'react';
import Tooltip from './Tooltip';

/**
 * Session Management component
 * @param {Object} props - Component props
 * @param {Object} props.formData - Form data state
 * @param {Function} props.handleChange - Function to handle form changes
 * @param {Object} props.tooltipDefinitions - Tooltip definitions
 * @returns {JSX.Element} Session Management component
 */
const SessionManagement = ({ formData, handleChange, tooltipDefinitions }) => {
  return (
    <div className={`border border-gray-200 rounded p-4 ${formData.saveSession ? 'bg-green-50' : 'bg-gray-50'} mb-6`}>
      <div className="flex items-center justify-between mb-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            id="saveSession"
            checked={formData.saveSession}
            onChange={handleChange}
            className="mr-2"
          />
          <Tooltip text={tooltipDefinitions.saveSession}>
            <span className="text-gray-700 font-semibold">Save Optimization Session</span>
          </Tooltip>
        </label>
      </div>

      {formData.saveSession && (
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-4">
            Save your optimization session to continue later or compare results with different configurations.
          </p>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="sessionName">
              <Tooltip text={tooltipDefinitions.sessionName}>
                Session Name:
              </Tooltip>
            </label>
            <input
              className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
              id="sessionName"
              type="text"
              placeholder="Enter a descriptive name for this session"
              value={formData.sessionName}
              onChange={handleChange}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
            >
              Load Session
            </button>
            <button
              type="button"
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
            >
              View Saved Sessions
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionManagement;
