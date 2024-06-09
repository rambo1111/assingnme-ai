from flask import Flask
from flask_cors import CORS
import requests
import time
import threading

app = Flask(__name__)
CORS(app)

def continuous_requests():
    while True:
        try:
            response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")
            print(response.text)
        except Exception as e:
            print(f"Error occurred: {e}")
        time.sleep(5)

@app.route('/')
def home():
    return 'Welcome to the Keep-Alive Service!'

if __name__ == '__main__':
    # Start the continuous requests in a separate thread
    threading.Thread(target=continuous_requests, daemon=True).start()
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=8080)
