from flask import Flask

app = Flask(__name__)

@app.route('/keep-alive')
def keep_alive():
    return 'Service is alive!'

if __name__ == '__main__':
    app.run(debug=True, port=8080)
