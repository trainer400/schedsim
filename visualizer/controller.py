from flask import Flask, render_template, request, jsonify
import os
import subprocess

app = Flask(__name__)

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

@app.route('/execute_main', methods=['POST'])
def execute_main():
    try:
        # Esegui il file test.py nella stessa directory
        # Esegui il file test.py nella stessa directory della directory principale che contiene visualizer
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
        input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'example_fifo.xml')
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'out_fifo.txt')

        result = subprocess.run(['python3', script_path, input_path, output_path], capture_output=True, text=True, check=True)
        
        # Restituisci l'output dell'esecuzione come risposta
        return jsonify({"output": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        # In caso di errore, restituisci un messaggio di errore dettagliato
        error_message = f"Error occurred: {e.stderr}\nStandard Output: {e.stdout}"
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 500
    except FileNotFoundError:
        error_message = "The specified file was not found."
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 404
    except Exception as e:
        # Gestione generica degli altri errori
        error_message = f"An unexpected error occurred: {str(e)}"
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 500

@app.route('/create_task', methods=['POST'])
def create_task():
    # Ricevi i dati del form per creare una nuova task
    real_time = request.form.get('realTime')
    task_type = request.form.get('taskType')
    task_id = request.form.get('taskId')
    period = request.form.get('period')
    activation = request.form.get('activation')
    deadline = request.form.get('deadline')
    wcet = request.form.get('wcet')

    # Esegui l'elaborazione per creare la nuova task
    # Ad esempio, puoi salvare i dati nel database o fare altre operazioni necessarie
    print(f'Real Time: {real_time}, Task Type: {task_type}, Task ID: {task_id}, Period: {period}, Activation: {activation}, Deadline: {deadline}, WCET: {wcet}')

    # Restituisci una risposta per confermare che la task è stata creata con successo
    return jsonify({'message': 'Task created successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
