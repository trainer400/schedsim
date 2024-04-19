from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

template_dir = os.path.abspath('front-end')
app = Flask(__name__, template_folder=template_dir)

@app.route('/message', methods=['POST'])
def receive_message():
    return jsonify({'response': 'Message received from JavaScript!'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)