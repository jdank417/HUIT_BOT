import requests
import json

url = "https://go.apis.huit.harvard.edu/ais-openai-direct/v1/chat/completions"
payload = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": "To what extent does scientific conservatism limit new discoveries?"
        }
    ],
    "temperature": 0.7
})
headers = {
    'Content-Type': 'application/json',
    'api-key': 'yourkeyhere'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
