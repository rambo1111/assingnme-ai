import requests
import time
import subprocess


cmd_command = "uvicorn main:app --host 0.0.0.0 --port 8000"
result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)

time.sleep(60)

while True:
  response = requests.get("https://test2-kfkt.onrender.com/keep-alive")
  print(response.text)
  time.sleep(60)
