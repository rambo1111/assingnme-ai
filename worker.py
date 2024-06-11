import requests
import time
import subprocess


cmd_command = "uvicorn main:app --host 0.0.0.0 --port 8000"
result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)

while True:
  response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")
  print(response.text)
