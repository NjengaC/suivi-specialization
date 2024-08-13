import requests
import os

def send_bulk_sms(mobile, message):
    url = "https://isms.celcomafrica.com/api/services/sendsms/"
    partner_id = os.getenv('PARTNER_ID')
    api_key = os.getenv('SMS_API_KEY')
    shortcode = "TEXTME"

    payload = {
        "partnerID": partner_id,
        "apikey": api_key,
        "mobile": mobile,
        "message": message,
        "shortcode": shortcode,
        "pass_type": "plain"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("SMS sent successfully!")
        return response.json()
    else:
        print(f"Failed to send SMS: {response.status_code}")
        return response.text
