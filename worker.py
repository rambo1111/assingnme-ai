from flask import Flask
import request
import time

app = Flask(__name__)

@app.route('/keep-alive')
def keep_alive():
    while True:
    response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")
    print(response.text)
    time.sleep(2)
    return 'Service is alive!'

if __name__ == '__main__':
    app.run(debug=True, port=8080)
