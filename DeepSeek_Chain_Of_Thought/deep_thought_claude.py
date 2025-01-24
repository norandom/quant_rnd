import requests
import os
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from termcolor import colored
from anthropic import Anthropic

# Constants
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Check if API keys are present
if not OPENROUTER_API_KEY:
    print(colored("Error: OPENROUTER_API_KEY environment variable is not set", "red"))
    exit(1)
if not ANTHROPIC_API_KEY:
    print(colored("Error: ANTHROPIC_API_KEY environment variable is not set", "red"))
    exit(1)

# Configure retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504]  # status codes to retry on
)

# Create session with retry strategy
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# Initialize Anthropic client for Claude
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

try:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/cascade",  # Adding referer for OpenRouter
        "X-Title": "Chain of Thought Demo"  # Adding title for OpenRouter
    }
    
    # Get user input and print it for verification
    user_question = input("Enter your question: ")
    print(colored(f"You asked: {user_question}", "cyan"))
    
    data = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {
                "role": "user",
                "content": user_question
            }
        ],
        "include_reasoning": True,
        "stream": True
    }

    print(colored("Sending request to OpenRouter API...", "cyan"))
    try:
        response = session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=(10, 90)  # (connect timeout, read timeout)
        )
        
        print(colored(f"Response status code: {response.status_code}", "cyan"))
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        print(colored("Error: Request timed out", "red"))
        exit(1)
    except requests.exceptions.RequestException as e:
        print(colored(f"Error making request: {str(e)}", "red"))
        exit(1)

    print(colored("Streaming response:", "green"))
    
    full_response = ""
    last_received = time.time()
    try:
        for line in response.iter_lines():
            if line:
                # Update last received time
                last_received = time.time()
                
                # Remove "data: " prefix and parse JSON
                json_str = line.decode('utf-8').removeprefix("data: ")
                
                if json_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(json_str)
                    if chunk['choices'][0]['delta'].get('content'):
                        content = chunk['choices'][0]['delta']['content']
                        print(content, end='', flush=True)
                        full_response += content
                except json.JSONDecodeError as e:
                    continue
                except KeyError as e:
                    continue
            
            # Check for timeout between chunks
            if time.time() - last_received > 30:  # 30 seconds timeout between chunks
                raise TimeoutError("No data received for 30 seconds")
                
    except TimeoutError as e:
        print(colored(f"\nError: {str(e)}", "red"))
        if full_response:
            print(colored("\nUsing partial response...", "yellow"))
        else:
            print(colored("No response received", "red"))
            exit(1)
    except Exception as e:
        print(colored(f"\nError while streaming response: {str(e)}", "red"))
        if full_response:
            print(colored("\nUsing partial response...", "yellow"))
        else:
            print(colored("No response received", "red"))
            exit(1)

    if not full_response.strip():
        print(colored("Error: Empty response received", "red"))
        exit(1)

    print("\n")
    # Extract reasoning from the full response
    reasoning = full_response  # The full response is now the reasoning

    # Pass to Claude for final answer
    print(colored("\nSending to Claude for final answer...", "cyan"))
    try:
        claude_response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"Given this reasoning about the technical problem:\n\n{reasoning}\n\nWhat is the correct answer?"
                }
            ]
        )
        
        print(colored(f"Debug - Claude response: {claude_response}", "yellow"))  # Debug print
        
        final_answer = claude_response.content[0].text
        print(colored("\nClaude's Final Answer:", "magenta"))
        print(final_answer)
        
    except Exception as e:
        print(colored(f"Error getting final answer from Claude: {str(e)}", "red"))
        exit(1)

except requests.exceptions.RequestException as e:
    print(colored(f"Request error: {str(e)}", "red"))
except Exception as e:
    print(colored(f"Unexpected error: {str(e)}", "red"))
