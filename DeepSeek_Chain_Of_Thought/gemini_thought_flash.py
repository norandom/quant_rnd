from google import genai
import os

""" 26.01.2025
The Google Gen AI SDK for Python 
https://ai.google.dev/gemini-api/docs/sdks#python-quickstart

pip install google-genai

NOT

pip install -q -U google-generativeai

This is a different package.
"""

# Get API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize the client with API key and version
client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version':'v1alpha'})

def get_chain_of_thought(prompt):
    """
    Make a request to the Gemini model and extract chain of thought.
    """
    try:
        # Configure thinking parameters
        config = {'thinking_config': {'include_thoughts': True}}
        
        # Make the request
        response = client.models.generate_content(
            model='gemini-2.0-flash-thinking-exp-1219',
            contents=prompt,
            config=config
        )
        
        # Extract thoughts and responses
        thoughts_and_responses = []
        for part in response.candidates[0].content.parts:
            if part.thought:
                thoughts_and_responses.append(f"Model Thought:\n{part.text}\n")
            else:
                thoughts_and_responses.append(f"\nModel Response:\n{part.text}\n")
        
        return "\n".join(thoughts_and_responses)
        
    except Exception as e:
        print(f"Error making API request: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    test_prompt = "Explain how RLHF works in simple terms."
    result = get_chain_of_thought(test_prompt)
    print(result)
