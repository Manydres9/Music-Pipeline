# LastFm API Example
import requests

url = "https://www.last.fm/api"
headers = {
    "Content-Type": "application/json"
}

response = requests.get(url)
data = response.json()
print(data)