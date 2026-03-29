from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def list_models():
    # It automatically finds GOOGLE_API_KEY in your environment
    client = genai.Client()
    
    print("--- Available Models for your API Key ---")
    for model in client.models.list():
        # Filtering for models that support text generation or embeddings
        print(f"Name: {model.name}")
        print(f"Supported Actions: {model.supported_actions}")
        print("-" * 30)

if __name__ == "__main__":
    list_models()