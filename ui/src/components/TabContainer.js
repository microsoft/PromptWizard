// TabContainer.js
import React, { useState } from 'react';
import TabList from './TabList';
import TabPanel from './TabPanel';

/**
 * TabContainer component for organizing content into tabs
 * @param {Object} props - Component props
 * @param {Array} props.tabs - Array of tab objects with label and content
 * @returns {JSX.Element} TabContainer component
 */
const TabContainer = ({ tabs }) => {
  const [value, setValue] = useState(0);

  const handleChange = (newValue) => {
    setValue(newValue);
  };

  return (
    <div className="w-full">
      <TabList
        id="prompt-wizard-tabs"
        value={value}
        onChange={handleChange}
        tabs={tabs}
      />
      {tabs.map((tab, index) => (
        <TabPanel
          key={index}
          value={value}
          index={index}
          id="prompt-wizard-tabs"
        >
          {tab.content}
        </TabPanel>
      ))}
    </div>
  );
};

export default TabContainer;
