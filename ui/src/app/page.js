'use client'

import { useState } from 'react';
import './globals.css'
import PromptForm from '../components/PromptForm';

export default function Home() {
  const [optimizedPrompt, setOptimizedPrompt] = useState('');

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-center">PromptWizard UI</h1>
      </header>

      <main className="max-w-4xl mx-auto">
        <div className="mb-8">
          <PromptForm setOptimizedPrompt={setOptimizedPrompt} />
        </div>

        <div className="mt-8 p-4 border rounded-lg bg-gray-50">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-semibold">Optimized Prompt:</h2>
            {optimizedPrompt && (
              <div className="flex items-center">
                {optimizedPrompt.includes("Additional instructions: Please ensure all responses are clear, concise") && (
                  <div className="mr-3 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                    Mock Response (No API Key)
                  </div>
                )}
                <button
                  onClick={() => {
                    // Create a blob with the optimized prompt
                    const blob = new Blob([optimizedPrompt], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);

                    // Create a temporary link and trigger download
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'optimized_prompt.txt';
                    document.body.appendChild(a);
                    a.click();

                    // Clean up
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                  }}
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                  Export Prompt
                </button>
              </div>
            )}
          </div>
          <pre className="whitespace-pre-wrap p-4 bg-white border rounded">
            {optimizedPrompt || 'Your optimized prompt will appear here'}
          </pre>

          {optimizedPrompt && optimizedPrompt.includes("Additional instructions: Please ensure all responses are clear, concise") && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
              <p className="font-semibold text-yellow-800">⚠️ This is a mock response</p>
              <p className="mt-1">The system is using a mock implementation because it couldn't access the Gemini API. To get real optimized prompts:</p>
              <ol className="list-decimal ml-5 mt-2 space-y-1">
                <li>Make sure you've entered a valid Gemini API key</li>
                <li>Click the "Validate" button next to the API key field</li>
                <li>Check that the API Key status shows as "Valid"</li>
              </ol>
              <p className="mt-2">You can get a Gemini API key from <a href="https://ai.google.dev/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">https://ai.google.dev/</a></p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
