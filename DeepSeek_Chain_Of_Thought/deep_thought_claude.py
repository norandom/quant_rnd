import requests
import os
import json
import time
import argparse
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from termcolor import colored
from anthropic import Anthropic
from openai import OpenAI

def check_lm_studio_available():
    try:
        response = requests.get("http://localhost:1234/v1/models")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def create_parser():
    parser = argparse.ArgumentParser(description='Chain of Thought with OpenRouter or Local LM Studio')
    parser.add_argument('--local', action='store_true', help='Use local LM Studio instead of OpenRouter')
    parser.add_argument('--verbose', action='store_true', help='Show detailed debug information')
    parser.add_argument('--o1', action='store_true', help='Use OpenAI O1 model for final answer instead of Claude')
    return parser

def get_api_client(use_local):
    if use_local:
        if not check_lm_studio_available():
            print(colored("Error: LM Studio is not running on http://localhost:1234", "red"))
            print(colored("Please start LM Studio and make sure it's running on port 1234", "red"))
            exit(1)
        print(colored("Using local LM Studio mode", "cyan"))
        base_url = "http://localhost:1234/v1"  # Added /v1 to match OpenAI format
        headers = {
            "Content-Type": "application/json"
        }
        return base_url, headers
    else:
        print(colored("Using OpenRouter mode", "cyan"))
        base_url = "https://openrouter.ai/api/v1"
        if not OPENROUTER_API_KEY:
            print(colored("Error: OPENROUTER_API_KEY environment variable is not set", "red"))
            exit(1)
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/cascade",
            "X-Title": "Chain of Thought Demo"
        }
        return base_url, headers

# Constants
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Parse arguments
parser = create_parser()
args = parser.parse_args()

print(colored(f"Running in {'local' if args.local else 'OpenRouter'} mode", "cyan"))

# Check required API keys
if not args.local and not OPENROUTER_API_KEY:
    print(colored("Error: OPENROUTER_API_KEY environment variable is not set", "red"))
    exit(1)

if args.o1:
    if not OPENAI_API_KEY:
        print(colored("Error: OPENAI_API_KEY environment variable is not set", "red"))
        exit(1)
    print(colored("Using OpenAI O1 for final answer", "cyan"))
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    if not ANTHROPIC_API_KEY:
        print(colored("Error: ANTHROPIC_API_KEY environment variable is not set", "red"))
        exit(1)
    print(colored("Using Claude for final answer", "cyan"))
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

# Create session with retry strategy
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def extract_think_content(text):
    """Extract content between <think> and </think> tags."""
    # Try to find content between think tags
    match = re.search(r'<think>(.*?)</think>', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If no think tags found, try to identify any structured thinking
    # Look for numbered steps, bullet points, or "Let's think step by step"
    step_patterns = [
        r"(?:Let's think step by step:?)(.*?)(?:\n\n|$)",
        r"(?:Step by step:?)(.*?)(?:\n\n|$)",
        r"(?:(?:\d+\.|[\*\-])\s+[^\n]+\n?)+",
    ]
    
    for pattern in step_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0).strip()
    
    # If no structured thinking found, return the original text
    return text

try:
    # Get API configuration based on mode
    base_url, headers = get_api_client(args.local)
    
    # Get user input and print it for verification
    user_question = input("Enter your question: ")
    print(colored(f"You asked: {user_question}", "cyan"))
    
    # Prepare the request data
    data = {
        "model": "deepseek-r1-distill-llama-8b" if args.local else "deepseek/deepseek-r1",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that thinks step by step. Always enclose your thinking process within <think></think> tags. After your thinking, provide a clear, concise answer."
            } if args.local else {
                "role": "system",
                "content": "You are a helpful assistant that thinks step by step."
            },
            {
                "role": "user",
                "content": user_question
            }
        ],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 2048
    }

    if not args.local:
        data["include_reasoning"] = True

    endpoint = f"{base_url}/chat/completions"
    print(colored(f"Sending request to {endpoint}...", "cyan"))
    if args.verbose:
        print(colored("Request details:", "cyan"))
        print(colored(f"- URL: {endpoint}", "cyan"))
        print(colored(f"- Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=2)}", "cyan"))
        print(colored(f"- Data: {json.dumps(data, indent=2)}", "cyan"))
    
    try:
        response = session.post(
            endpoint,
            headers=headers,
            json=data,
            stream=True,
            timeout=(10, 90)  # (connect timeout, read timeout)
        )
        
        print(colored(f"Response status code: {response.status_code}", "cyan"))
        if args.verbose:
            print(colored(f"Response headers: {dict(response.headers)}", "cyan"))
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        print(colored("Error: Request timed out", "red"))
        exit(1)
    except requests.exceptions.RequestException as e:
        print(colored(f"Error making request: {str(e)}", "red"))
        if args.verbose and hasattr(e, 'response') and e.response is not None:
            print(colored(f"Response text: {e.response.text}", "red"))
        exit(1)

    print(colored("\nStreaming response:", "green"))
    
    full_response = ""
    raw_response = ""  # Store the complete raw response for think tag extraction
    last_received = time.time()
    try:
        for line in response.iter_lines():
            if line:
                # Update last received time
                last_received = time.time()
                
                # Debug raw line
                decoded_line = line.decode('utf-8')
                if args.verbose:
                    print(colored(f"\nDebug - Raw line: {decoded_line}", "yellow"))
                
                # Remove "data: " prefix if present
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                else:
                    json_str = decoded_line
                
                if json_str == "[DONE]":
                    break
                    
                try:
                    chunk = json.loads(json_str)
                    if args.verbose:
                        print(colored(f"Debug - Parsed chunk: {json.dumps(chunk, indent=2)}", "yellow"))
                    
                    if args.local:
                        # Local LM Studio format
                        if 'choices' in chunk and chunk['choices']:
                            choice = chunk['choices'][0]
                            if 'delta' in choice:
                                content = choice['delta'].get('content', '')
                            else:
                                content = choice.get('text', '')
                    else:
                        # OpenRouter format
                        content = chunk['choices'][0]['delta'].get('content', '')
                    
                    if content:
                        if args.local:
                            raw_response += content  # Accumulate raw response
                            # Only print content between think tags if we have them
                            if '<think>' in content or '</think>' in content or '<think>' in raw_response:
                                print(content, end='', flush=True)
                        else:
                            print(content, end='', flush=True)
                        full_response += content
                except json.JSONDecodeError as e:
                    if args.verbose:
                        print(colored(f"\nJSON decode error: {str(e)} for line: {json_str}", "red"))
                    continue
                except KeyError as e:
                    if args.verbose:
                        print(colored(f"\nKey error: {str(e)} in chunk: {chunk}", "red"))
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
    if args.local:
        reasoning = extract_think_content(raw_response)
        if reasoning != raw_response:
            print(colored("\nExtracted thinking process:", "cyan"))
            print(reasoning)
    else:
        reasoning = full_response

    # Pass to final answer model (Claude or O1)
    if args.verbose:
        print(colored(f"\nSending to {'OpenAI O1' if args.o1 else 'Claude'} for final answer...", "cyan"))
    
    try:
        if args.o1:
            response = openai_client.chat.completions.create(
                model="o1",
                messages=[
                    {
                        "role": "user",
                        "content": f"Given this reasoning about the technical problem:\n\n{reasoning}\n\nWhat is the correct answer?"
                    }
                ],
                reasoning_effort="high"
            )
            final_answer = response.choices[0].message.content
        else:
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
            final_answer = claude_response.content[0].text
            
        print(colored(f"\n{'OpenAI O1' if args.o1 else 'Claude'}'s Final Answer:", "magenta"))
        print(final_answer)
        
    except Exception as e:
        print(colored(f"Error getting final answer: {str(e)}", "red"))
        exit(1)

except requests.exceptions.RequestException as e:
    print(colored(f"Request error: {str(e)}", "red"))
except Exception as e:
    print(colored(f"Unexpected error: {str(e)}", "red"))
