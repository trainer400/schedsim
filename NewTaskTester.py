import xml.etree.ElementTree as ET
import xml.dom.minidom
import SchedIO
import Task
import random

MAX_TIME_START = 20
MAX_TIME_END = 100
MAX_PERIOD = 40
MAX_WCET = 20
MAX_QUANTUM = 10
TASKS_NUMS = 10
NEW_TASKS_NUMS = 4

def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        content_file1 = f1.read()
        content_file2 = f2.read()
    if content_file1 == content_file2:
        print("Correct")
    else:
        print("Not correct")

def create_xml_structure():
    doc = xml.dom.minidom.Document()

    # Create the simulation root
    simulation = doc.createElement("simulation")
    doc.appendChild(simulation)

    # Create the attributes
    time = doc.createElement("time")
    simulation.appendChild(time)
    software = doc.createElement("software")
    simulation.appendChild(software)
    tasks = doc.createElement("tasks")
    software.appendChild(tasks)
    scheduler = doc.createElement("scheduler")
    software.appendChild(scheduler)
    hardware = doc.createElement("hardware")
    simulation.appendChild(hardware)
    cpus = doc.createElement("cpus")
    hardware.appendChild(cpus)
    pe = doc.createElement("pe")
    cpus.appendChild(pe)

    return (doc, time, tasks, scheduler, pe)

if __name__ == "__main__":
    algorithms = ["FIFO", "SJF", "HRRN", "SRFT", "RR", "RM", "DM"]

    # Test equality for all the scheduling algorithms
    for alg in algorithms:

        # Create the two XML documents
        (doc1, time1, tasks1, scheduler1, pe1) = create_xml_structure()
        (doc2, time2, tasks2, scheduler2, pe2) = create_xml_structure()

        # Set the PE directly to default TODO: if need, change here to change number of processors
        pe1.setAttribute("id", "0")
        pe1.setAttribute("speed", "1")
        pe2.setAttribute("id", "0")
        pe2.setAttribute("speed", "1")
        
        # Select random times for the simulation
        start_time = random.randint(0, MAX_TIME_START)
        end_time = random.randint(start_time + 1, MAX_TIME_END)
        add_time = random.randint(1, MAX_TIME_END)

        # Set the computed times
        time1.setAttribute("start", str(start_time))
        time1.setAttribute("end", str(end_time))
        time2.setAttribute("start", str(start_time))
        time2.setAttribute("end", str(end_time))

        new_tasks = []

        # Add the tasks
        for task_id in range(1, TASKS_NUMS + 1):
            real_time = random.randint(0, 1) == 1
            real_time_str = str(real_time).lower()

            type = "sporadic" if random.randint(0, 1) == 0 else "periodic"
            sporadic_task = type == "sporadic"
            activation = None
            period = None
            deadline = None
            wcet = None

            # Set the task properties depending on its type
            if type == "sporadic":
                activation = random.randint(start_time, end_time - 1)
                deadline = random.randint(activation + 1, MAX_TIME_END)
                wcet = random.randint(1, max(1, deadline - 1))
            else:
                period = random.randint(1, MAX_PERIOD)
                deadline = random.randint(start_time + 1, MAX_TIME_END)
                wcet = random.randint(1, max(1, min(period, deadline)))

            # Add the task inside the tasks object
            task1 = doc1.createElement("task")
            tasks1.appendChild(task1)

            task1.setAttribute("real_time", real_time_str)
            task1.setAttribute("type", type)
            task1.setAttribute("id", str(task_id))
            task1.setAttribute("activation" if sporadic_task else "period", str(activation) if sporadic_task else str(period))
            task1.setAttribute("wcet", str(wcet))
            if real_time or not sporadic_task:
                task1.setAttribute("deadline", str(deadline))
            
            # If the task2 is one of the XML ones, add it
            if task_id <= TASKS_NUMS - NEW_TASKS_NUMS:
                task2 = doc1.createElement("task")
                tasks2.appendChild(task2)

                task2.setAttribute("real_time", real_time_str)
                task2.setAttribute("type", type)
                task2.setAttribute("id", str(task_id))
                task2.setAttribute("activation" if sporadic_task else "period", str(activation) if sporadic_task else str(period))
                task2.setAttribute("wcet", str(wcet))
                if real_time or not sporadic_task:
                    task2.setAttribute("deadline", str(deadline))
            
            # In case not, add it to the list of tasks that are then added at runtime
            else:
                new_task = Task.Task(real_time, type, task_id, period if not sporadic_task else None, activation if sporadic_task else None, deadline, wcet)
                new_tasks.append(new_task)
    
        # if alg != "RR":
        #     scheduler1 = ET.SubElement(software1, "scheduler", algorithm=alg)
        #     scheduler1.tail = "\n"
        #     scheduler2 = ET.SubElement(software2, "scheduler", algorithm=alg)
        #     scheduler2.tail = "\n"
        # else:
        #     quantum = random.randint(1, MAX_QUANTUM)
        #     scheduler1 = ET.SubElement(software1, "scheduler", algorithm=alg, quantum=str(quantum))
        #     scheduler1.tail = "\n"
        #     scheduler2 = ET.SubElement(software2, "scheduler", algorithm=alg, quantum=str(quantum))
        #     scheduler2.tail = "\n"
        # hardware1 = ET.SubElement(simulation1, "hardware")
        # hardware2 = ET.SubElement(simulation2, "hardware")
        # cpus1 = ET.SubElement(hardware1, "cpus")
        # cpus1.tail = "\n"
        # cpus2 = ET.SubElement(hardware2, "cpus")
        # cpus2.tail = "\n"
        # pe1 = ET.SubElement(cpus1, "pe", id="0", speed="1")
        # pe1.tail = "\n"
        # pe2 = ET.SubElement(cpus2, "pe", id="0", speed="1")
        # pe2.tail = "\n"
        # tree1 = ET.ElementTree(simulation1)
        # tree1.write("examples/Inputs/test_input1.xml", encoding="UTF-8", xml_declaration=True)
        # tree2 = ET.ElementTree(simulation2)
        # tree2.write("examples/Inputs/test_input2.xml", encoding="UTF-8", xml_declaration=True)

        # test_scheduler1 = SchedIO.import_file("examples/Inputs/test_input1.xml", "examples/Outputs/test_output1.csv")
        # test_scheduler1.execute()
        # test_scheduler1.terminate()
        # test_scheduler2 = SchedIO.import_file("examples/Inputs/test_input2.xml", "examples/Outputs/test_output2.csv")
        # test_scheduler2.execute()

        # count = 0
        # for new_task in new_tasks:
        #     test_scheduler2.new_task(new_task)
        #     test_scheduler2.terminate()
        #     count += 1
        # test_scheduler2.add_time(add_time)
        # test_scheduler2.terminate()

        # compare_files("examples/Outputs/test_output1.csv", "examples/Outputs/test_output2.csv")
