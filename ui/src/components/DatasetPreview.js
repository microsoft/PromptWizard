// DatasetPreview.js
import React, { useState } from 'react';

/**
 * Dataset Preview component
 * @param {Object} props - Component props
 * @param {Object} props.dataset - Dataset to preview
 * @returns {JSX.Element} Dataset Preview component
 */
const DatasetPreview = ({ dataset }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  
  if (!dataset || dataset.length === 0) {
    return (
      <div className="border border-gray-200 rounded p-4 bg-gray-50 mb-6">
        <h3 className="text-lg font-semibold mb-2">Dataset Preview</h3>
        <p className="text-gray-500">No dataset available for preview.</p>
      </div>
    );
  }

  // Calculate pagination
  const totalPages = Math.ceil(dataset.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, dataset.length);
  const currentItems = dataset.slice(startIndex, endIndex);

  return (
    <div className="border border-gray-200 rounded p-4 bg-gray-50 mb-6">
      <h3 className="text-lg font-semibold mb-2">Dataset Preview</h3>
      <p className="text-sm text-gray-500 mb-4">
        Showing {startIndex + 1}-{endIndex} of {dataset.length} examples
      </p>
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead>
            <tr className="bg-gray-100">
              <th className="py-2 px-4 border-b text-left">#</th>
              <th className="py-2 px-4 border-b text-left">Input</th>
              <th className="py-2 px-4 border-b text-left">Output</th>
            </tr>
          </thead>
          <tbody>
            {currentItems.map((item, index) => (
              <tr key={startIndex + index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                <td className="py-2 px-4 border-b">{startIndex + index + 1}</td>
                <td className="py-2 px-4 border-b">
                  <div className="max-h-20 overflow-y-auto">
                    {item.input || (item.question ? item.question : 'N/A')}
                  </div>
                </td>
                <td className="py-2 px-4 border-b">
                  <div className="max-h-20 overflow-y-auto">
                    {item.output || (item.answer ? item.answer : 'N/A')}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-4">
          <button
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <span className="text-sm">
            Page {currentPage} of {totalPages}
          </span>
          <button
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default DatasetPreview;
