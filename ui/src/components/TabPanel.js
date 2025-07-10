import React from 'react';

/**
 * TabPanel component for creating tabbed interfaces
 * @param {Object} props - Component props
 * @param {string} props.id - Unique identifier for the tab panel
 * @param {number} props.value - Current active tab index
 * @param {number} props.index - This tab's index
 * @param {React.ReactNode} props.children - Tab content
 * @returns {JSX.Element} Tab panel component
 */
const TabPanel = (props) => {
  const { children, value, index, id, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`${id}-tabpanel-${index}`}
      aria-labelledby={`${id}-tab-${index}`}
      className="p-4 border border-t-0 border-gray-200 rounded-b-lg bg-white"
      {...other}
    >
      {value === index && <div>{children}</div>}
    </div>
  );
};

export default TabPanel;
