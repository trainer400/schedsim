import math
import copy
from abc import *
import SchedEvent
import SchedIO


class Scheduler:

    def __init__(self, output_file):
        self.name = 'GenericScheduler'
        self.tasks = []
        self.start = None
        self.end = None

        self.executing = None

        self.arrival_events = []
        self.finish_events = []
        self.deadline_events = []
        self.start_events = []

        self.size = 0
        self.time_list = []
        self.arrival_events_list = []
        self.finish_events_list = []
        self.deadline_events_list = []
        self.start_events_list = []
        self.executing_list = []

        self.arrival_events_at_time = []
        self.finish_events_at_time = []
        self.deadline_events_at_time = []
        self.start_events_at_time = []
        self.executing_at_time = []

        self.quantum_counter_at_time = []

        self.output_file = SchedIO.SchedulerEventWriter(output_file)

        self.cores = []

        self.event_id = 0



    @abstractmethod
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def find_finish_events(self, time):
        pass

    def get_all_arrivals(self):
        arrival_events = []
        for task in self.tasks:
            # Here you can add the code to choose between different cores:
            task.core = self.cores[0].id
            # ------------------------------- #
            if task.type == 'periodic':
                i = self.start
                j = 1
                while i < self.end:
                    event = SchedEvent.ScheduleEvent(i, task, SchedEvent.EventType.activation.value, self.event_id)
                    self.event_id += 1
                    event.job = j
                    arrival_events.append(event)
                    i += task.period
                    j += 1
            elif task.type == 'sporadic':
                task.init = task.activation
                event = SchedEvent.ScheduleEvent(task.activation, task, SchedEvent.EventType.activation.value, self.event_id)
                self.event_id += 1
                arrival_events.append(event)
        arrival_events.sort(key=lambda x: x.timestamp)
        return arrival_events

    def find_arrival_event(self, time):
        helper_list = []
        for event in self.arrival_events:
            if event.timestamp == time:
                self.output_file.add_scheduler_event(event)
                start_event = SchedEvent.ScheduleEvent(
                    event.timestamp, event.task, SchedEvent.EventType.start.value, event.id)
                start_event.job = event.job
                self.start_events.append(start_event)
            elif event.timestamp > time:
                helper_list.append(event)
        self.arrival_events = helper_list

    def find_deadline_events(self, time):
        helper_list = []
        for event in self.deadline_events:
            if event.timestamp == time:
                self.output_file.add_scheduler_event(event)
            elif event.timestamp > time:
                helper_list.append(event)
        self.deadline_events = helper_list


class NonPreemptive(Scheduler):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'GenericNonPreemptiveScheduler'

    def execute(self):
        pass

    def find_finish_events(self, time):
        helper_list = []
        for event in self.finish_events:
            if event.timestamp == time:
                self.output_file.add_scheduler_event(event)
                self.executing = None
            elif event.timestamp > time:
                helper_list.append(event)
        self.finish_events = helper_list

    def find_start_events(self, time):
        helper_list = []
        for event in self.start_events:
            if event.timestamp == time and self.executing is None:
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create finish event:
                finish_timestamp = event.timestamp + event.task.wcet
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, event.task, SchedEvent.EventType.finish.value, event.id)
                finish_event.job = event.job
                self.finish_events.append(finish_event)
                # Create deadline event:
                if event.task.real_time:
                    deadline_timestamp = event.timestamp + event.task.deadline
                    deadline_event = SchedEvent.ScheduleEvent(
                        deadline_timestamp, event.task, SchedEvent.EventType.deadline.value, event.id)
                    deadline_event.job = event.job
                    self.deadline_events.append(deadline_event)
            elif event.timestamp == time and self.executing:
                event.timestamp += (self.executing.timestamp + self.executing.task.wcet - event.timestamp)
            if event.timestamp > time:
                helper_list.append(event)
        self.start_events = helper_list


class Preemptive(Scheduler):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'GenericPreemptiveScheduler'

    def execute(self):
        pass

    def find_finish_events(self, time):
        if self.executing:
            if self.executing.executing_time == self.executing.task.wcet:
                # Create finish event:
                finish_event = SchedEvent.ScheduleEvent(
                    time, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)
                # Delete from start_events:
                self.start_events.remove(self.executing)
                # Free execute:
                self.executing = None

    def create_deadline_event(self, event):
        if event.task.real_time:
            deadline_timestamp = event.timestamp + event.task.deadline
            deadline_event = SchedEvent.ScheduleEvent(
                deadline_timestamp, event.task, SchedEvent.EventType.deadline.value, event.id)
            deadline_event.job = event.job
            self.deadline_events.append(deadline_event)
            event.task.first_time_executing = False


def debug(self, time):
    return
    print('-------------------------')
    print('time ' + str(time))
    print('finish')
    for ev in self.finish_events:
        print(ev.task.id, ev.remaining_time, ev.executing_time, ev.timestamp, ev.task.wcet, ev.task.first_time_executing)
    print('deadline')
    for ev in self.deadline_events:
        print(ev.task.id, ev.remaining_time, ev.executing_time, ev.timestamp, ev.task.wcet, ev.task.first_time_executing)
    print('arrival')
    for ev in self.arrival_events:
        print(ev.task.id, ev.remaining_time, ev.executing_time, ev.timestamp, ev.task.wcet, ev.task.first_time_executing)
    print('start')
    for ev in self.start_events:
        print(ev.task.id, ev.remaining_time, ev.executing_time, ev.timestamp, ev.task.wcet, ev.task.first_time_executing)
    print('executing')
    if(self.executing == None):
        print('None')
    else:
        print(self.executing.task.id, self.executing.remaining_time, self.executing.executing_time, self.executing.task.first_time_executing)

def search_pos(self, time):
    for i in range(len(self.time_list) - 1):
        if self.time_list[i] <= time and self.time_list[i + 1] > time:
            return i
    return len(self.time_list) - 1

def delete(self, time):
    if(self.time_list[-1] >= time):
        self.time_list.pop()
        self.arrival_events_list.pop()
        self.finish_events_list.pop()
        self.deadline_events_list.pop()
        self.start_events_list.pop()
        self.executing_list.pop()
        delete(self, time)

def reset(self):
    self.executing = None
    self.finish_events = []
    self.deadline_events = []
    self.arrival_events = []
    self.start_events = []
    self.time_list = []
    self.finish_events_list = []
    self.deadline_events_list = []
    self.arrival_events_list = []
    self.start_events_list = []


class FIFO(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'FIFO'

    def compute(self, time, count):
        while time <= self.end:
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                if self.executing:
                    self.executing_list.append(True)
                else:
                    self.executing_list.append(False)
                self.finish_events_list.append(copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                count = 0
            time += 1
        debug(self, time)

    def execute(self):
        self.arrival_events = self.get_all_arrivals()
        self.size = int(math.sqrt(self.end))
        count = self.size - 1
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        new_task.core = self.cores[0].id
        time = 0
        count = 0
        if new_task.type == 'sporadic' and new_task.activation > 0:
            time = new_task.activation
            pos = search_pos(self, time - 1)
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])
            if self.executing:
                self.executing = self.start_events[0]
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
            self.arrival_events.append(event)
            # Sort by timestamp
            self.start_events.sort(key=lambda x: x.timestamp)
            delete(self, time)
            time = self.time_list[pos] + 1
        else:
            reset(self)
            self.event_id = 0
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1
        self.output_file.clean(time)
        self.compute(time, count)

    def terminate(self):
        self.output_file.terminate_write()


class SJF(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'SJF'

    def compute(self, time, count):
        while time <= self.end:
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Sort by wcet
            self.start_events.sort(key=lambda x: x.task.wcet)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                if self.executing:
                    self.executing_list.append(True)
                else:
                    self.executing_list.append(False)
                self.finish_events_list.append(copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                count = 0
            time += 1
        debug(self, time)

    def execute(self):
        self.arrival_events = self.get_all_arrivals()
        self.size = int(math.sqrt(self.end))
        count = self.size - 1
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        new_task.core = self.cores[0].id
        time = 0
        count = 0
        if new_task.type == 'sporadic' and new_task.activation > 0:
            time = new_task.activation
            pos = search_pos(self, time - 1)
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])
            if self.executing:
                self.executing = self.start_events[0]
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
            self.arrival_events.append(event)
            # Sort by wcet
            self.start_events.sort(key=lambda x: x.task.wcet)
            delete(self, time)
            time = self.time_list[pos] + 1
        else:
            reset(self)
            self.event_id = 0
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1
        self.output_file.clean(time)
        self.compute(time, count)

    def terminate(self):
        self.output_file.terminate_write()


class HRRN(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'HRRN'

    def compute(self, time, count):
        while time <= self.end:
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.calculate_responsive_ratio(time)
            # Sort by response ratio:
            self.start_events.sort(key=lambda x: x.response_ratio, reverse=True)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                if self.executing:
                    self.executing_list.append(True)
                else:
                    self.executing_list.append(False)
                self.finish_events_list.append(copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                count = 0
            time += 1
        debug(self, time)

    def execute(self):
        self.arrival_events = self.get_all_arrivals()
        self.size = int(math.sqrt(self.end))
        count = self.size - 1
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        new_task.core = self.cores[0].id
        time = 0
        count = 0
        if new_task.type == 'sporadic' and new_task.activation > 0:
            time = new_task.activation
            pos = search_pos(self, time - 1)
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])
            if self.executing:
                self.executing = self.start_events[0]
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
            self.arrival_events.append(event)
            # Sort by response ratio:
            self.start_events.sort(key=lambda x: x.response_ratio, reverse=True)
            delete(self, time)
            time = self.time_list[pos] + 1
        else:
            reset(self)
            self.event_id = 0
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1
        self.output_file.clean(time)
        self.compute(time, count)

    def calculate_responsive_ratio(self, time):
        for event in self.start_events:
            if event.init <= time:
                w = time - event.init
                c = event.task.wcet
                event.response_ratio = (w + c)/c

    def terminate(self):
        self.output_file.terminate_write()


class SRTF(Preemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'ShortestRemainingTimeFirst'

    def calculate_remaining_time(self):
        for event in self.start_events:
            event.remaining_time = event.task.wcet - event.executing_time

    def choose_executed(self, time):
        if len(self.start_events) > 0:
            self.start_events.sort(key=lambda x: x.remaining_time)
            # Non task is executed:
            if self.executing is None:
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event:
                self.create_deadline_event(event)
            # Change of task:
            elif self.executing.remaining_time > self.start_events[0].remaining_time and \
                    self.executing.id != self.start_events[0].id:
                # Create finish event of the current task in execution:
                finish_timestamp = time
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)
                # Change task:
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event:
                if event.task.first_time_executing:
                    self.create_deadline_event(event)

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.calculate_remaining_time()
            self.choose_executed(time)
            if self.executing:
                self.executing.executing_time += 1
                self.executing_at_time.append(copy.deepcopy(self.executing))
            else:
                self.executing_at_time.append(None)
            self.finish_events_at_time.append(copy.deepcopy(self.finish_events))
            self.deadline_events_at_time.append(copy.deepcopy(self.deadline_events))
            self.arrival_events_at_time.append(copy.deepcopy(self.arrival_events))
            self.start_events_at_time.append(copy.deepcopy(self.start_events))
            time += 1
        debug(self, time)


    def new_task(self, new_task):
        new_task.core = self.cores[0].id
        time = 0
        if new_task.type == 'sporadic' and new_task.activation > 0:
            time = new_task.activation
            # Go back in time
            self.finish_events = copy.deepcopy(self.finish_events_at_time[time - 1])
            self.deadline_events = copy.deepcopy(self.deadline_events_at_time[time - 1])
            self.arrival_events = copy.deepcopy(self.arrival_events_at_time[time - 1])
            self.start_events = copy.deepcopy(self.start_events_at_time[time - 1])
            self.executing = copy.deepcopy(self.executing_at_time[time - 1])
            if self.executing:
                self.executing = self.start_events[0]
                '''for event in self.start_events:
                    if event.id == self.executing.id:
                        self.executing = event'''
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1
            for t in range(time):
                self.arrival_events_at_time[t].append(copy.deepcopy(event))
                self.arrival_events_at_time[t].sort(key=lambda x: x.timestamp)
            self.arrival_events.append(event)
            self.arrival_events.sort(key=lambda x: x.timestamp)
        else:
            self.executing = None
            self.finish_events = []
            self.deadline_events = []
            self.arrival_events = []
            self.start_events = []
            self.tasks.append(new_task)
            for task in self.tasks:
                task.first_time_executing = True
                task.finish = False
            self.arrival_events = self.get_all_arrivals()

        self.output_file.clean(time)
        while (time <= self.end):
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.calculate_remaining_time()
            self.choose_executed(time)
            if self.executing:
                self.executing.executing_time += 1
                self.executing_at_time[time] = copy.deepcopy(self.executing)
            else:
                self.executing_at_time[time] = None
            self.finish_events_at_time[time] = copy.deepcopy(self.finish_events)
            self.deadline_events_at_time[time] = copy.deepcopy(self.deadline_events)
            self.arrival_events_at_time[time] = copy.deepcopy(self.arrival_events)
            self.start_events_at_time[time] = copy.deepcopy(self.start_events)
            time += 1
        debug(self, time)

    def terminate(self):
        self.output_file.terminate_write()


class RoundRobin(Preemptive):

    def __init__(self, output_file, quantum):
        super().__init__(output_file)
        self.name = 'RoundRobin'
        self.quantum = int(quantum)
        self.quantum_counter = 0

    def choose_executed(self, time):
        if len(self.start_events) > 0:
            # Non task is executed:
            if self.executing is None:
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event:
                self.create_deadline_event(event)
                # Restart quantum counter
                self.quantum_counter = 0
            # Change of task:
            elif self.quantum_counter == self.quantum:
                # Create finish event of the current task in execution:
                finish_timestamp = time
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)
                # Change task:
                # 1) Delete from start_events:
                del self.start_events[0]
                # 2) Add this event to the final:
                self.start_events.append(copy.deepcopy(self.executing))
                # 3) New event:
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event:
                if event.task.first_time_executing:
                    self.create_deadline_event(event)
                # Restart counter
                self.quantum_counter = 0

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.choose_executed(time)
            self.quantum_counter += 1
            self.quantum_counter_at_time.append(copy.deepcopy(self.quantum_counter))
            if self.executing:
                self.executing.executing_time += 1
                self.executing_at_time.append(copy.deepcopy(self.executing))
            else:
                self.executing_at_time.append(None)
            self.finish_events_at_time.append(copy.deepcopy(self.finish_events))
            self.deadline_events_at_time.append(copy.deepcopy(self.deadline_events))
            self.arrival_events_at_time.append(copy.deepcopy(self.arrival_events))
            self.start_events_at_time.append(copy.deepcopy(self.start_events))
            time += 1
        debug(self, time)

    def new_task(self, new_task):
        new_task.core = self.cores[0].id
        time = 0
        if new_task.type == 'sporadic' and new_task.activation > 0:
            time = new_task.activation
            # Go back in time
            self.finish_events = copy.deepcopy(self.finish_events_at_time[time - 1])
            self.deadline_events = copy.deepcopy(self.deadline_events_at_time[time - 1])
            self.arrival_events = copy.deepcopy(self.arrival_events_at_time[time - 1])
            self.start_events = copy.deepcopy(self.start_events_at_time[time - 1])
            self.executing = copy.deepcopy(self.executing_at_time[time - 1])
            self.quantum_counter = copy.deepcopy(self.quantum_counter_at_time[time - 1])
            if self.executing:
                for event in self.start_events:
                    if event.id == self.executing.id:
                        self.executing = event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1
            for t in range(time):
                self.arrival_events_at_time[t].append(copy.deepcopy(event))
                self.arrival_events_at_time[t].sort(key=lambda x: x.timestamp)
            self.arrival_events.append(event)
            self.arrival_events.sort(key=lambda x: x.timestamp)
        else:
            self.executing = None
            self.finish_events = []
            self.deadline_events = []
            self.arrival_events = []
            self.start_events = []
            self.quantum_counter = 0
            self.tasks.append(new_task)
            for task in self.tasks:
                task.first_time_executing = True
                task.finish = False
            self.arrival_events = self.get_all_arrivals()

        self.output_file.clean(time)
        while (time <= self.end):
            debug(self, time)
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.choose_executed(time)
            self.quantum_counter += 1
            self.quantum_counter_at_time[time] = copy.deepcopy(self.quantum_counter)
            if self.executing:
                self.executing.executing_time += 1
                self.executing_at_time[time] = copy.deepcopy(self.executing)
            else:
                self.executing_at_time[time] = None
            self.finish_events_at_time[time] = copy.deepcopy(self.finish_events)
            self.deadline_events_at_time[time] = copy.deepcopy(self.deadline_events)
            self.arrival_events_at_time[time] = copy.deepcopy(self.arrival_events)
            self.start_events_at_time[time] = copy.deepcopy(self.start_events)
            time += 1
        debug(self, time)

    def terminate(self):
        self.output_file.terminate_write()