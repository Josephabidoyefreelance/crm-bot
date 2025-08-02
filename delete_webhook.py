import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key safely from environment variables
CLOSE_API_KEY = os.getenv("CLOSE_IO_API_KEY")
WEBHOOK_ID = "whsub_5DVojT0hIrl3808kBBnhS7"

url = f"https://api.close.com/api/v1/webhook/{WEBHOOK_ID}/"

response = requests.delete(url, auth=(CLOSE_API_KEY, ""))

print("Status Code:", response.status_code)
print("Response:", response.text)
