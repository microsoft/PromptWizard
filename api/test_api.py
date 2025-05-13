import requests
import json

def test_optimize_prompt_api():
    """Test the optimize_prompt API endpoint."""
    url = "http://localhost:5000/api/optimize_prompt"
    
    # Test data
    data = {
        "taskDescription": "Test task description",
        "baseInstruction": "This is a test prompt that needs optimization.",
        "answerFormat": "JSON",
        "model": "Gemini",
        "mutationRounds": 2,
        "refineSteps": 1,
        "useExamples": False,
        "dataset": "Custom",
        "evaluationCriteria": ["Clarity", "Accuracy"]
    }
    
    # Send request
    print("Sending request to API...")
    response = requests.post(url, json=data)
    
    # Print results
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Success:", result["success"])
        print("\nOptimized prompt:")
        print(result["optimizedPrompt"])
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    test_optimize_prompt_api()
