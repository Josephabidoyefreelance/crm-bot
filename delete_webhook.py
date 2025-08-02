import requests

CLOSE_API_KEY = "api_2syo0UnYRkhah2CxWw9fxI.380io3msbLAsxh6EaqMl4B"
WEBHOOK_ID = "whsub_5DVojT0hIrl3808kBBnhS7"

url = f"https://api.close.com/api/v1/webhook/{WEBHOOK_ID}/"

response = requests.delete(url, auth=(CLOSE_API_KEY, ""))

print("Status Code:", response.status_code)
print("Response:", response.text)
