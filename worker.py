import requests
import time

while True:
    response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")
    # print(response.text)
    time.sleep(2)
