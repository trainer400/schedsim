from flask import Flask, render_template, request, jsonify
import os
import sys
import matplotlib
matplotlib.use('Agg')  # Imposta il backend non interattivo

# Aggiungi la cartella padre al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import SchedIO
import Scheduler, Task
from Visualizer import create_graph

app = Flask(__name__)

scheduler = None
@app.route('/')
def index():
    return render_template('index.html', title='schedsim')

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

    return jsonify({'message': 'XML File uploaded successfully!', 'file_path': save_path}), 200

@app.route('/execute_main', methods=['POST'])
def execute_main():
    try:
        
        # Verifica che il content type sia application/json
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        # Ottieni il percorso del file XML dal corpo della richiesta
        input_path = request.json.get('file_path')
        if not input_path:
            return jsonify({"error": "No input file path provided"}), 400
        
        output_path = os.path.join(os.path.dirname(input_path), 'out.csv')
        
        # Importa e esegui lo scheduler
        scheduler = SchedIO.import_file(input_path, 'input/out.csv')
        scheduler.execute()
        
        #create_graph('static/out.png')
        # Restituisci l'output dell'esecuzione come risposta
        return jsonify({"output": "Execution completed!"}), 200

    except FileNotFoundError:
        error_message = "The specified file was not found."
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 404
    except Exception as e:
        # Gestione generica degli altri errori
        error_message = f"An unexpected error occurred: {str(e)}"
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 500
    
    finally:
        # Elimina il file di input e altri file generati
        if 'input_path' in locals():
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
            except Exception as e:
                app.logger.error(f"Error occurred while deleting the file: {str(e)}")

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

    # Controlla che i valori ricevuti siano validi
    if not all([real_time, task_type, task_id, period, activation, deadline, wcet]):
        return jsonify({'error': 'All fields are required.'}), 400

    # Converte i valori in tipi appropriati
    try:
        task_id = int(task_id)
        period = int(period)
        activation = int(activation)
        deadline = int(deadline)
        wcet = int(wcet)
    except ValueError:
        return jsonify({'error': 'Invalid input format.'}), 400

    # Esegui ulteriori controlli sui valori
    if task_id <= 0:
        return jsonify({'error': 'Task ID must be a positive integer.'}), 400
    if wcet <= 0:
        return jsonify({'error': 'WCET must be a positive integer.'}), 400
    if (task_type == 'periodic' and period <= 0) or (task_type == 'sporadic' and activation < 0):
        return jsonify({'error': 'Invalid period or activation value.'}), 400
    if deadline <= 0:
        return jsonify({'error': 'Deadline must be a positive integer.'}), 400
    if period <= deadline and task_type == 'periodic':
        return jsonify({'error': 'Period must be greater than deadline.'}), 400
    if wcet > period and task_type == 'periodic':
        return jsonify({'error': 'WCET must be less than or equal to period.'}), 400
    if deadline < wcet:
        return jsonify({'error': 'Deadline must be greater than WCET.'}), 400

    print(f'Real Time: {real_time}, Task Type: {task_type}, Task ID: {task_id}, Period: {period}, Activation: {activation}, Deadline: {deadline}, WCET: {wcet}')

    new_task = Task.Task(real_time, task_type, task_id, period, activation, deadline, wcet)
    scheduler = SchedIO.import_file("input/example_srtf.xml", "input/out.csv")
    scheduler.execute()
    scheduler.new_task(new_task)
    
    # Restituisci una risposta per confermare che la task è stata creata con successo
    return jsonify({'message': 'Task created successfully!'}), 200

@app.route('/print_graph', methods=['POST'])
def print_graph():
    # Qui puoi aggiungere le operazioni necessarie per stampare il grafico
    try:
        create_graph('static/out.png')
        return jsonify({'message': 'Graph printed successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

