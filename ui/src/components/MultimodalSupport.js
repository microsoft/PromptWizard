// MultimodalSupport.js
import React, { useState } from 'react';
import Tooltip from './Tooltip';

/**
 * Multimodal Support component
 * @param {Object} props - Component props
 * @param {Object} props.formData - Form data state
 * @param {Function} props.handleChange - Function to handle form changes
 * @param {Object} props.tooltipDefinitions - Tooltip definitions
 * @returns {JSX.Element} Multimodal Support component
 */
const MultimodalSupport = ({ formData, handleChange, tooltipDefinitions }) => {
  const [imagePreview, setImagePreview] = useState(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className={`border border-gray-200 rounded p-4 ${formData.enableMultimodal ? 'bg-blue-50' : 'bg-gray-50'} mb-6`}>
      <div className="flex items-center justify-between mb-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            id="enableMultimodal"
            checked={formData.enableMultimodal}
            onChange={handleChange}
            className="mr-2"
          />
          <Tooltip text={tooltipDefinitions.enableMultimodal}>
            <span className="text-gray-700 font-semibold">Enable Multimodal Support</span>
          </Tooltip>
        </label>
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Beta Feature</span>
      </div>

      {formData.enableMultimodal && (
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-4">
            Upload an image to optimize prompts for image-based tasks. This allows the model to understand visual context.
          </p>

          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Upload Reference Image
              </label>
              <div className="flex items-center">
                <label className="flex items-center justify-center px-4 py-2 bg-blue-100 text-blue-700 rounded cursor-pointer hover:bg-blue-200">
                  <span className="text-sm font-medium">Select Image</span>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleImageUpload}
                  />
                </label>
              </div>
            </div>

            <div className="flex-1">
              {imagePreview ? (
                <div className="mt-2">
                  <p className="text-sm font-medium mb-2">Image Preview:</p>
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="max-w-full h-auto max-h-40 border border-gray-300 rounded"
                  />
                </div>
              ) : (
                <div className="mt-2 border border-dashed border-gray-300 rounded p-4 text-center text-gray-500">
                  <p>No image selected</p>
                  <p className="text-xs">Supported formats: JPG, PNG, GIF</p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Image Description Task Type
            </label>
            <select
              className="appearance-none block w-full bg-white text-gray-700 border border-gray-300 rounded py-2 px-3 leading-tight focus:outline-none focus:border-blue-500"
              id="imageTaskType"
            >
              <option value="description">Image Description</option>
              <option value="classification">Image Classification</option>
              <option value="captioning">Image Captioning</option>
              <option value="vqa">Visual Question Answering</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default MultimodalSupport;
