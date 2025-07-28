import os
from dotenv import load_dotenv

load_dotenv()

print("OpenAI Key:", os.getenv("OPENAI_API_KEY"))
print("Close.io Key:", os.getenv("CLOSE_API_KEY"))
