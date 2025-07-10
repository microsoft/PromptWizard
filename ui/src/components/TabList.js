// TabList.js
import React from 'react';

/**
 * TabList component for creating tabbed interfaces
 * @param {Object} props - Component props
 * @param {string} props.id - Unique identifier for the tab list
 * @param {number} props.value - Current active tab index
 * @param {Function} props.onChange - Function to handle tab change
 * @param {Array} props.tabs - Array of tab objects with label
 * @returns {JSX.Element} Tab list component
 */
const TabList = ({ id, value, onChange, tabs }) => {
  return (
    <div className="border-b border-gray-200">
      <ul className="flex flex-wrap -mb-px text-sm font-medium text-center" role="tablist">
        {tabs.map((tab, index) => (
          <li key={index} className="mr-2" role="presentation">
            <button
              className={`inline-block p-4 border-b-2 rounded-t-lg ${
                value === index
                  ? 'text-blue-600 border-blue-600 active'
                  : 'hover:text-gray-600 hover:border-gray-300 border-transparent'
              }`}
              id={`${id}-tab-${index}`}
              type="button"
              role="tab"
              aria-controls={`${id}-tabpanel-${index}`}
              aria-selected={value === index}
              onClick={() => onChange(index)}
            >
              {tab.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TabList;
