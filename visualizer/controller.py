
from flask import Flask, render_template, request
import os, subprocess

app = Flask(__name__)


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


@app.route('/upload_xml', methods=['POST'])
def upload_xml():
    # Controlla se il form ha un file
    if 'xmlFile' not in request.files:
        return 'No file part'

    xml_file = request.files['xmlFile']
    
    # Salva il file XML nella directory 'input/'
    xml_file.save(os.path.join("input/", xml_file.filename))

    return 'XML File uploaded successfully!'

@app.route('/execute_function', methods=['POST'])
def execute_function():
    print("tutto funziona lancio main.py")
    

if __name__ == '__main__':
    app.run(debug=True, port=5001)


