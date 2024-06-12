import requests
import time
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start_server():
    cmd_command = "uvicorn main:app --reload"
    result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to start server: {result.stderr}")
    else:
        logging.info("Server started successfully")

def keep_alive():
    while True:
        try:
            response = requests.get("https://test2-kfkt.onrender.com/keep-alive")
            logging.info(f"Keep-alive response: {response.text}")
        except Exception as e:
            logging.error(f"Error occurred during keep-alive request: {e}")
        time.sleep(60)

if __name__ == "__main__":
    start_server()
    time.sleep(60)  # Initial delay before starting the keep-alive loop
    keep_alive()
