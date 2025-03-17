import os
from dotenv import load_dotenv
from portkey_ai import Portkey

# Load environment variables
load_dotenv()

# Initialize Portkey clients
portkey_anthropic = Portkey(
    api_key=os.getenv("PORTKEY_API_KEY"),
    virtual_key=os.getenv("PORTKEY_VIRTUAL_KEY_ANTHROPIC")
)

portkey_openai = Portkey(
    api_key=os.getenv("PORTKEY_API_KEY"),
    virtual_key=os.getenv("PORTKEY_VIRTUAL_KEY_OPENAI")
)

portkey_google = Portkey(
    api_key=os.getenv("PORTKEY_API_KEY"),
    virtual_key=os.getenv("PORTKEY_VIRTUAL_KEY_GOOGLE")
)

def claude35sonnet(prompt):
    """Wrapper function for Claude 3.5 Sonnet"""
    completion = portkey_anthropic.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="claude-3-5-sonnet-latest",
        max_tokens=8192
    )
    return completion.choices[0].message.content

def claude37sonnet(prompt):
    """Wrapper function for Claude 3.7 Sonnet"""
    completion = portkey_anthropic.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="claude-3-7-sonnet-latest",
        max_tokens=8192
    )
    return completion.choices[0].message.content

def gpt4o(prompt):
    """Wrapper function for GPT-4"""
    completion = portkey_openai.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4o",
        max_tokens=8192
    )
    return completion.choices[0].message.content

def gemini2pro(prompt):
    """Wrapper function for Gemini 2 Pro"""
    completion = portkey_google.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gemini-2.0-pro-exp-02-05",
        max_tokens=8192
    )
    return completion.choices[0].message.content

def gemini2flashthinking(prompt):
    """Wrapper function for Gemini 2 Flash Thinking"""
    completion = portkey_google.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gemini-2.0-flash-thinking-exp-01-21",
        max_tokens=8192
    )
    return completion.choices[0].message.content

def o3minihigh(prompt):
    """Wrapper function for o3-mini-high model"""
    completion = portkey_openai.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="o3-mini-2025-01-31"
    )
    return completion.choices[0].message.content

def test():
    # Test Claude 3.5 Sonnet
    claude_response = claude35sonnet("What is the meaning of life?")
    print("Claude 3.5 Sonnet response:", claude_response)
    
    # Test Claude 3.7 Sonnet
    claude37_response = claude37sonnet("What is the meaning of life?")
    print("Claude 3.7 Sonnet response:", claude37_response)
    
    # Test GPT-4
    gpt4_response = gpt4o("What is the meaning of life?")
    print("GPT-4 response:", gpt4_response)
    
    # Test Gemini 2 Pro
    gemini_response = gemini2pro("What is the meaning of life?")
    print("Gemini 2 Pro response:", gemini_response)

    # Test Gemini 2 Flash Thinking
    gemini_flash_response = gemini2flashthinking("What is the meaning of life?")
    print("Gemini 2 Flash Thinking response:", gemini_flash_response)
