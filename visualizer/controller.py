
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
        return 'No file part', 400

    xml_file = request.files['xmlFile']
    
    # Verifica se è stato selezionato un file
    if xml_file.filename == '':
        return 'No selected file', 400
    
    # Salva il file XML nella directory 'input/'
    save_path = os.path.join("input", xml_file.filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    xml_file.save(save_path)

    return 'XML File uploaded successfully!', 200

@app.route('/execute_function', methods=['POST'])
def execute_function():
    try:
        # Esegui il comando per lanciare il file main.py
        result = subprocess.run(['python', 'main.py'], capture_output=True, text=True, check=True)
        return result.stdout, 200
    except subprocess.CalledProcessError as e:
        return f"Error occurred: {e.stderr}", 500

@app.route('/create_task', methods=['POST'])
def create_task():
    # Ricevi i dati del form per creare una nuova task
    task_name = request.form.get('taskName')
    task_description = request.form.get('taskDescription')

    # Esegui l'elaborazione per creare la nuova task
    # Ad esempio, puoi salvare i dati nel database o fare altre operazioni necessarie

    # Restituisci una risposta per confermare che la task è stata creata con successo
    return jsonify({'message': 'Task created successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)


