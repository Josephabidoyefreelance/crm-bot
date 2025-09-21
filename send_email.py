import requests

POSTMARK_TOKEN ="9e32dc24-fd27-499d-8c27-e14353cb75de"  # must match verified server

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Postmark-Server-Token": POSTMARK_TOKEN
}

data = {
    "From": "bgn@ciphus.io",

  # verified sender
    "To": "bgn@ciphus.io", "bgn@stacksoft.com" "bgn@ciphus.com"  # same verified sender as recipient
    "Subject": "Hello 4 Postmark",
    "HtmlBody": "<p>465701ab-e4e6-493e-b1bc-e96faf6d3c9e@mtasv.net.</p>",
    "TextBody": "Hello, this is a test email all the 4 emails are working correctly."
}

try:
    response = requests.post("https://api.postmarkapp.com/email", headers=headers, json=data)
    response.raise_for_status()
    print("✅ Email sent:", response.json())
except requests.exceptions.RequestException as e:
    print("❌ Error sending email:", e)
# Ensure you have the requests library installed:
