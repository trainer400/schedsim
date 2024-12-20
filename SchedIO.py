import xml.etree.ElementTree as ET
from ServerScheduler import *
import Task
import Scheduler
import Cpu


def import_file(file_path, output_file) -> Scheduler.Scheduler:
    scheduler = None
    root_node = ET.parse(file_path).getroot()

    # Parsing SCHEDULER parametres based on TAG xml
    for node in root_node.findall('./software/scheduler'):
        if scheduler is not None:
            raise Exception('More than one scheduler is defined in the file')
        algorithm = node.attrib.get('algorithm')
        if algorithm == 'RR':
            quantum = node.attrib.get('quantum')
            if quantum is None:
                raise Exception('No "quantum" attribute defined in the file')
            scheduler = Scheduler.RoundRobin(output_file, quantum)
        elif algorithm == 'FIFO':
            scheduler = Scheduler.FIFO(output_file)
        elif algorithm == 'SJF':
            scheduler = Scheduler.SJF(output_file)
        elif algorithm == 'HRRN':
            scheduler = Scheduler.HRRN(output_file)
        elif algorithm == 'SRTF':
            scheduler = Scheduler.SRTF(output_file)
        elif algorithm == 'RM':
            scheduler = Scheduler.RateMonotonic(output_file)

            # Select the server algorithm for asynchronous tasks
            server_algorithm = node.attrib.get("server")
            server_capacity = node.attrib.get("capacity")
            server_period = node.attrib.get("period")

            # Check server validity
            if server_algorithm is None or server_capacity is None or server_period is None:
                raise Exception(
                    'No "server/capacity/period" attributes for asynchronous tasks')

            # Create the server instance
            server = None
            if server_algorithm == "polling":
                server = PollingServer(int(server_capacity), int(server_period))
            elif server_algorithm == "deferrable":
                server = DeferrableServer(int(server_capacity), int(server_period))
            else:
                raise Exception(
                    f"Invalid server algorithm: {server_algorithm}")

            # Set the server algorithm instance
            scheduler.set_server_scheduler(server)

        elif algorithm == 'DM':
            scheduler = Scheduler.DeadlineMonotonic(output_file)
        else:
            raise Exception(f'Invalid scheduler algorithm: {algorithm}')

    if scheduler is None:
        raise Exception('No scheduler is defined in the file')

    # Parsing the TASKS based on the TAG xml
    for node in root_node.findall('./software/tasks/task'):
        _real_time = node.attrib.get('real_time', 'false') == 'true'
        _type = node.attrib['type']
        _id = int(node.attrib['id'])
        _period = int(node.attrib.get('period', -1))
        _activation = int(node.attrib.get('activation', -1))
        _deadline = int(node.attrib.get('deadline', -1))
        _wcet = int(node.attrib['wcet'])

        if _id < 0 or _wcet <= 0 or (_type == 'periodic' and _period <= 0) or (_type == 'sporadic' and _activation < 0):
            raise Exception('Non-positive values are saved in the file')

        if (_wcet > _period != -1) or (_deadline != -1 and _deadline < _wcet):
            raise Exception('Inconsistent values are saved in the file')

        # Create the task with the parsed options
        task = Task.Task(_real_time, _type, _id, _period,
                         _activation, _deadline, _wcet)

        # Add the task to the scheduler list
        scheduler.tasks.append(task)

    if not scheduler.tasks:
        raise Exception('No tasks recognized in the file')

    # Parsing time
    time_node = root_node.find('./time')
    if time_node is not None:
        scheduler.start = int(time_node.attrib['start'])
        scheduler.end = int(time_node.attrib['end'])
        if scheduler.end < scheduler.start:
            raise Exception('Error in time definition')

    # Parsing hardware
    for node in root_node.findall('./hardware/cpus/pe'):
        _id = node.attrib['id']
        core = Cpu.Core(_id)
        core_speed = node.attrib.get('speed')
        if core_speed:
            core.speed = core_speed
        scheduler.cores.append(core)

    if not scheduler.cores:
        raise Exception('No cores recognized in the file')

    return scheduler


class SchedulerEventWriter:
    def __init__(self, output_file):
        self.out = open(output_file, 'w')
        self.out.write(
            'timestamp, task, job, processor, type_of_event, extra_data' + '\n')

    def add_scheduler_event(self, scheduler_event):
        self.out.write(
            str(scheduler_event.timestamp) + ',' + str(scheduler_event.task.id) + ',' +
            str(scheduler_event.job) + ',' + str(scheduler_event.processor) + ',' +
            str(scheduler_event.type) + ',' + str(scheduler_event.extra) + '\n')

    # Function to clean the data in the output file between [time,end]
    def clean(self, time):
        self.out.close()
        # Create a list for save the element in the range [0,time]
        events = []
        # Open the file of output and read it to save the element, where is valid "events_time<=time"
        with open(self.out.name, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if parts[0] == 'timestamp':
                    events.append(line)
                else:
                    event_time = int(parts[0])
                    if event_time < time:
                        events.append(line)
        self.out = open(self.out.name, 'w')
        self.out.writelines(events)

    # Function to close the file used by Scheduler
    def terminate_write(self):
        self.out.close()
