"""Check available models on GitHub Models"""
import os
from openai import OpenAI

# Get API key from environment or user input
api_key = os.environ.get('GITHUB_TOKEN') or input("Enter your GitHub token: ")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key
)

try:
    # Try to list models
    models = client.models.list()
    print("\n=== Available Models ===")
    for model in models:
        print(f"- {model.id}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying some common model names...")
    
    # Test common model names
    test_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4",
        "claude-3-5-sonnet",
        "claude-3.5-sonnet",
        "Claude-3.5-Sonnet",
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "Mistral-large",
        "Mistral-large-2411",
        "AI21-Jamba-1.5-Large",
        "AI21-Jamba-1.5-Mini",
        "Cohere-command-r",
        "Cohere-command-r-08-2024",
        "Cohere-command-r-plus",
        "Cohere-command-r-plus-08-2024",
        "Meta-Llama-3.1-405B-Instruct",
        "Meta-Llama-3.1-70B-Instruct",
        "Meta-Llama-3.1-8B-Instruct",
        "Meta-Llama-3-70B-Instruct",
        "Meta-Llama-3-8B-Instruct",
        "Phi-3.5-MoE-instruct",
        "Phi-3.5-mini-instruct",
        "Phi-3.5-vision-instruct",
        "Phi-3-medium-128k-instruct",
        "Phi-3-medium-4k-instruct",
        "Phi-3-mini-128k-instruct",
        "Phi-3-mini-4k-instruct",
        "Phi-3-small-128k-instruct",
        "Phi-3-small-8k-instruct"
    ]
    
    print("\nTesting models by attempting a simple call...")
    for model_name in test_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=5
            )
            print(f"✓ {model_name} - WORKS")
        except Exception as e:
            if "unknown_model" in str(e).lower():
                print(f"✗ {model_name} - Unknown model")
            elif "rate" in str(e).lower() or "quota" in str(e).lower():
                print(f"? {model_name} - Exists but rate limited")
            else:
                print(f"? {model_name} - Error: {str(e)[:50]}")
