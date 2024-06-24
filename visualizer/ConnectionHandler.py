from flask import Flask, render_template, request, jsonify
import os
import sys
import matplotlib
from SchedulerController import SchedulerController

matplotlib.use('Agg')  # Imposta il backend non interattivo

# Aggiungi la cartella padre al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import SchedIO
import Task
from Visualizer import create_graph

app = Flask(__name__)
# Specifica il percorso del file di output
output_file_path = 'input/out.csv'
scheduler_controller = SchedulerController(output_file_path)

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
    scheduler_controller.load_xml_file(save_path)
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
    
        success = scheduler_controller.execute_scheduler()
        if not success:
            return jsonify({"error": "Error executing scheduler"}), 500

        return jsonify({"output": "Execution completed!"}), 200

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
    if period >= deadline and task_type == 'periodic':
        return jsonify({'error': 'Period must be greater than deadline.'}), 400
    if wcet > period and task_type == 'periodic':
        return jsonify({'error': 'WCET must be less than or equal to period.'}), 400
    if deadline < wcet:
        return jsonify({'error': 'Deadline must be greater than WCET.'}), 400

    print(f'Real Time: {real_time}, Task Type: {task_type}, Task ID: {task_id}, Period: {period}, Activation: {activation}, Deadline: {deadline}, WCET: {wcet}')
    if(task_type=="sporadic"):
        success = scheduler_controller.create_task([real_time, task_type, task_id, activation, deadline, wcet])
    elif(task_type=="periodic"):
        success = scheduler_controller.create_task([real_time, task_type, task_id, period, activation, deadline, wcet])
    if success:
        return jsonify({'message': 'Task created successfully!'}), 200
    else:
        return jsonify({'error': 'Error creating task.'}), 500

@app.route('/print_graph', methods=['POST'])
def print_graph():
    try:
        success = scheduler_controller.print_graph()
        if success:
            return jsonify({'message': 'Graph printed successfully!'}), 200
        else:
            return jsonify({'error': 'Error printing graph.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_xml', methods=['POST'])
def create_xml():
    try:
        # Ricevi i dati dal corpo della richiesta
        start = request.form.get('start')
        end = request.form.get('end')
        scheduling_algorithm = request.form.get('schedulingAlgorithm')
        task_number = int(request.form.get('taskNumber'))

        tasks = []
        for i in range(task_number):
            task_type = request.form.get(f'taskType{i}')  
            task_id = request.form.get(f'taskId{i}') 
            period = request.form.get(f'period{i}')  
            activation = request.form.get(f'activation{i}') 
            deadline = request.form.get(f'deadline{i}') 
            wcet = request.form.get(f'wcet{i}') 

            # Verifica se i valori sono validi
            if not all([task_type, task_id, period, activation, deadline, wcet]):
                return jsonify({'error': 'All task fields are required.'}), 400

            # Converte i valori in interi, se possibile
            try:
                task_id = int(task_id)
                period = int(period)
                activation = int(activation)
                deadline = int(deadline)
                wcet = int(wcet)
            except ValueError:
                return jsonify({'error': 'Invalid input format for task fields.'}), 400

            # Aggiungi i dati della task alla lista
            task = {
                "real_time": True,
                "type": task_type,
                "id": task_id,
                "period": period,
                "activation": activation,
                "deadline": deadline,
                "wcet": wcet
            }
            tasks.append(task)

        # Esegui la creazione del file XML utilizzando il metodo create_xml di SchedulerController
        xml_path = scheduler_controller.create_xml("input/example.xml", int(start), int(end), tasks, scheduling_algorithm, 0, 1)

        if xml_path:
            return jsonify({'message': 'XML file created successfully!', 'xml_path': xml_path}), 200
        else:
            return jsonify({'error': 'Failed to create XML file.'}), 500

    except Exception as e:
        # Gestione generica degli altri errori
        error_message = f"An unexpected error occurred: {str(e)}"
        app.logger.error(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
