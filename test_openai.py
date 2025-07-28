import os
from dotenv import load_dotenv
import openai

# Load .env file
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")

print("OpenAI Key Loaded:", api_key is not None)

# Set key
openai.api_key = api_key

# Test the key
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say hello from the bot!"}
        ],
        temperature=0
    )
    print("✅ OpenAI is working!")
    print("Response:", response['choices'][0]['message']['content'])
except Exception as e:
    print("❌ OpenAI API call failed:")
    print(e)
