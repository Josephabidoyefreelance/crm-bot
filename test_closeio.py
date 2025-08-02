import requests

api_key = "api_2syo0UnYRkhah2CxWw9fxI.380io3msbLAsxh6EaqMl4B"  # Replace with your actual new API key

url = "https://api.close.com/api/v1/me/"

response = requests.get(url, auth=(api_key, ''))

print("Status:", response.status_code)
print("Response:", response.json())
