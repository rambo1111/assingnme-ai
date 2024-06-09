from flask import Flask
import requests
import time
import threading

app = Flask(__name__)

def continuous_requests():
    while True:
        response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")
        print(response.text)
        time.sleep(2)

@app.route('/keep-alive')
def keep_alive():
    return 'Service is alive!'

if __name__ == '__main__':
    # Start the continuous requests in a separate thread
    threading.Thread(target=continuous_requests, daemon=True).start()
    # Run the Flask app
    app.run(debug=True, port=8080)

