#add create xml
from flask import Flask, render_template, request, jsonify
import os
import sys
import matplotlib
import xml.etree.ElementTree as ET
import xml.dom.minidom
import xmltodict



matplotlib.use('Agg')  # Imposta il backend non interattivo

# Aggiungi la cartella padre al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import SchedIO
import Task
from Visualizer import create_graph
app = Flask(__name__)
class SchedulerController:
    def __init__(self, output_file=None):
        self.scheduler = None
        self.output_file = output_file

    def load_xml_file(self, file_path):
        try:
            self.scheduler = SchedIO.import_file(file_path, self.output_file)
            return True
        except FileNotFoundError:
            print("File not found.")
            return False

    def execute_scheduler(self):
        if self.scheduler:
            self.scheduler.execute()
            return True
        else:
            print("Scheduler not loaded.")
            return False

    def create_task(self, task_data):
        if self.scheduler:
            new_task = Task.Task(*task_data)
            self.scheduler.new_task(new_task)
            return True
        else:
            print("Scheduler not loaded.")
            return False

    def print_graph(self):
        try:
             # Verifica se il file out.csv esiste
            if not os.path.exists('input/out.csv'):
                raise FileNotFoundError("out.csv file not found.")
            create_graph('static/out.png')
            return True
        except Exception as e:
            print(f"Error printing graph: {str(e)}")
            return False

    
    def create_xml(self, file_path, start, end, tasks, scheduling_algorithm, cpu_pe_id, cpu_speed):
        try:
            # Creazione del documento XML
            doc = xml.dom.minidom.Document()
            simulation = doc.createElement("simulation")
            doc.appendChild(simulation)

            # Aggiunta del nodo per il tempo di simulazione
            time = doc.createElement("time")
            time.setAttribute("start", str(start))
            time.setAttribute("end", str(end))
            simulation.appendChild(time)

            # Aggiunta del nodo per il software (tasks e scheduler)
            software = doc.createElement("software")
            simulation.appendChild(software)

            tasks_node = doc.createElement("tasks")
            software.appendChild(tasks_node)

            # Aggiunta dei nodi per ogni task
            for task_data in tasks:
                task = doc.createElement("task")
                for key, value in task_data.items():
                    task.setAttribute(key, str(value))
                tasks_node.appendChild(task)

            # Aggiunta del nodo per lo scheduler
            scheduler = doc.createElement("scheduler")
            scheduler.setAttribute("algorithm", scheduling_algorithm)
            if scheduling_algorithm == "RR":
                scheduler.setAttribute("quantum", "3")
            software.appendChild(scheduler)

            # Aggiunta del nodo per l'hardware (cpus)
            hardware = doc.createElement("hardware")
            simulation.appendChild(hardware)

            cpus = doc.createElement("cpus")
            hardware.appendChild(cpus)

            pe = doc.createElement("pe")
            pe.setAttribute("id", str(cpu_pe_id))
            pe.setAttribute("speed", str(cpu_speed))
            cpus.appendChild(pe)

            # Scrittura del documento XML su file
            with open(file_path, "w", encoding="utf-8") as xml_file:
                doc.writexml(xml_file, indent="\t", newl="\n", addindent="\t", encoding="utf-8")

            return file_path
        except Exception as e:
            print(f"Error creating XML file: {str(e)}")
            return None
        