import { useState } from 'react';

const Tooltip = ({ text, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-block">
      <div
        className="inline-flex items-center"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
        <span className="ml-1 text-blue-500 text-xs cursor-help">ⓘ</span>
      </div>

      {isVisible && (
        <div className="absolute z-10 w-56 p-2 mt-1 text-xs text-gray-700 bg-white border border-gray-200 rounded shadow-md transition-opacity duration-200 ease-in-out">
          <div className="max-h-32 overflow-y-auto">
            {text}
          </div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;
