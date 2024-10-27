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

        self.starting_arrivals = []
        self.size = 0
        self.time_list = []

        # Snapshots that are saved every sqrt(time)
        self.arrival_events_list = []
        self.finish_events_list = []
        self.deadline_events_list = []
        self.start_events_list = []
        self.executing_list = []

        self.quantum_counter_at_time = []

        self.quantum_counter_list = []

        self.output_file = SchedIO.SchedulerEventWriter(output_file)

        self.cores = []

        self.event_id = 0

    # TODO: Why two?
    @abstractmethod
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def find_finish_events(self, time):
        pass

    def get_all_arrivals(self):
        '''
            Arrivals are all the events that are ready to be scheduled\n
            @return A sorted array of all the events
        '''
        arrival_events = []
        for task in self.tasks:
            # Here you can add the code to choose between different cores:
            task.core = self.cores[0].id
            # ------------------------------- #
            if task.type == 'periodic':
                timestamp = self.start
                job = 1

                # Generate N copies of the event due to its periodicity
                while timestamp < self.end:
                    event = SchedEvent.ScheduleEvent(
                        timestamp, task, SchedEvent.EventType.activation.value, self.event_id)
                    self.event_id += 1

                    event.job = job
                    job += 1

                    arrival_events.append(event)
                    timestamp += task.period

            elif task.type == 'sporadic':
                # Add one event corresponding to the inserted task because of it needs to be executed once
                task.init = task.activation
                event = SchedEvent.ScheduleEvent(
                    task.activation, task, SchedEvent.EventType.activation.value, self.event_id)
                self.event_id += 1
                arrival_events.append(event)

        # Sort sporadic and periodic events by execution timestamp
        arrival_events.sort(key=lambda x: x.timestamp)
        return arrival_events

    def add_arrivals(self, time_start, time_end):
        '''
            Adds a task into the arrival list only if it is periodic\n
            @param time_start TODO
            @param time_end TODO
        '''
        for task in self.tasks:
            # Here you can add the code to choose between different cores:
            task.core = self.cores[0].id
            # ------------------------------- #
            if task.type == 'periodic':
                timestamp = self.start
                job = 1

                while timestamp < time_end:
                    # Add the event if the considered timestamp comes after the specified start time
                    if timestamp >= time_start:
                        event = SchedEvent.ScheduleEvent(
                            timestamp, task, SchedEvent.EventType.activation.value, self.event_id)

                        self.event_id += 1
                        event.job = job

                        # Add the event in all the already saved snapshots and sort them again
                        for arrival_events in self.arrival_events_list:
                            arrival_events.append(copy.deepcopy(event))
                            arrival_events.sort(key=lambda x: x.timestamp)

                    timestamp += task.period
                    job += 1

    def find_arrival_event(self, time):
        '''
            Finds the events that are corresponding to the passed timestamp. Those events are inserted
            in the start_events list and removed from the arrival_events list.\n
            @param time current time
        '''
        helper_list = []

        for event in self.arrival_events:
            # In case of current event, add it in the start_events array and remove it from arrival_events array
            if event.timestamp == time:
                # Log the event
                self.output_file.add_scheduler_event(event)

                # Add it to the start events
                start_event = SchedEvent.ScheduleEvent(
                    event.timestamp, event.task, SchedEvent.EventType.start.value, event.id)
                start_event.job = event.job
                self.start_events.append(start_event)

            # In case of future events, insert them again into the arrival_events without touching them
            elif event.timestamp > time:
                helper_list.append(event)

        self.arrival_events = helper_list

    def find_deadline_events(self, time):
        '''
            Deadline events are those events that missed their deadline\n
            @param time current time
        '''
        helper_list = []

        for event in self.deadline_events:
            if event.timestamp == time:
                # Log the event
                self.output_file.add_scheduler_event(event)

            # Append again the event in the list if it has not been processed yet
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
        '''
            Finish events are events that are completing their execution.\n
            The method logs when the events terminate\n
            @param time current time
        '''
        helper_list = []
        for event in self.finish_events:
            if event.timestamp == time:
                # Log the event
                self.output_file.add_scheduler_event(event)
                self.executing = None

            # Append again the event in the list if it not finished yet
            elif event.timestamp > time:
                helper_list.append(event)

        self.finish_events = helper_list

    def find_start_events(self, time):
        '''
            Starts one task in start_events list and creates the finish/deadline events.
            @param time current time
        '''
        helper_list = []

        for event in self.start_events:
            # If not already executing something and the event has to be executed now then execute it
            if event.timestamp == time and self.executing is None:
                # Log the event
                self.output_file.add_scheduler_event(event)
                self.executing = event

                # Create finish event
                finish_timestamp = event.timestamp + event.task.wcet
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, event.task, SchedEvent.EventType.finish.value, event.id)
                finish_event.job = event.job
                self.finish_events.append(finish_event)

                # Create deadline event for real time tasks
                if event.task.real_time:
                    deadline_timestamp = event.timestamp + event.task.deadline
                    deadline_event = SchedEvent.ScheduleEvent(
                        deadline_timestamp, event.task, SchedEvent.EventType.deadline.value, event.id)
                    deadline_event.job = event.job
                    self.deadline_events.append(deadline_event)

            # If the event is scheduled for the execution now but something is already in execution, shift the execution timestamp
            elif event.timestamp == time and self.executing:
                event.timestamp += (self.executing.timestamp +
                                    self.executing.task.wcet - event.timestamp)

            # At the end, if the event is out of time, it gets appended again into the start event list
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
        '''
            Finish events are events that are completing their execution.\n
            The method logs when the events terminate\n
            @param time current time
        '''
        if self.executing:
            # If the total execution time is respected, terminate the event
            if self.executing.executing_time == self.executing.task.wcet:
                # Create finish event
                finish_event = SchedEvent.ScheduleEvent(
                    time, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)

                # Delete from start_events
                for event in self.start_events:
                    if event.id == self.executing.id:
                        self.start_events.remove(event)

                # Free execute
                self.executing = None

    def create_deadline_event(self, event):
        '''
            In case of real time events, it creates a deadline event to specify wether a task exceeds its deadline\n
            @param event the event to which the deadline must correspond
        '''
        if event.task.real_time:
            deadline_timestamp = event.timestamp + event.task.deadline
            deadline_event = SchedEvent.ScheduleEvent(
                deadline_timestamp, event.task, SchedEvent.EventType.deadline.value, event.id)
            deadline_event.job = event.job

            # Append the event
            self.deadline_events.append(deadline_event)
            event.task.first_time_executing = False


def search_pos(self, time):
    '''
        Looks inside the snapshots list what is the last saved snapshot given the current time
    '''
    for i in range(len(self.time_list) - 1):
        if self.time_list[i] <= time and self.time_list[i + 1] > time:
            return i
    return len(self.time_list) - 1


def delete(self, time):
    if (self.time_list[-1] >= time):
        self.time_list.pop()
        self.arrival_events_list.pop()
        self.finish_events_list.pop()
        self.deadline_events_list.pop()
        self.start_events_list.pop()
        self.executing_list.pop()
        if self.name == 'RoundRobin':
            self.quantum_counter_list.pop()
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
    self.executing_list = []
    if self.name == 'ShortestRemainingTimeFirst' or self.name == 'RoundRobin':
        for task in self.tasks:
            task.first_time_executing = True
            task.finish = False
    if self.name == 'RoundRobin':
        self.quantum_counter = 0
        self.quantum_counter_list = []


class FIFO(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'FIFO'

    def compute(self, time, count):
        '''
            The function computes the scheduling actions starting from time and count
            @param time starting time
            @param count snapshot counter
        '''
        # For every time step compute the algorithm
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.find_start_events(time)

            # When the snapshot counter is sqrt(end - start) save the state
            count += 1
            if count == self.size:
                self.time_list.append(time)
                self.finish_events_list.append(
                    copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(
                    copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(
                    copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                self.executing_list.append(copy.deepcopy(self.executing))
                count = 0
            time += 1

    def execute(self):
        '''
            The function executes the entire algorithm, preparing the number of snapshot size and the arrival events
        '''
        # Get all the events that need to be scheduled
        self.arrival_events = self.get_all_arrivals()

        # Set the number of steps
        self.size = int(math.sqrt(self.end - self.start))

        # The first snapshot must be saved at time 0
        count = self.size - 1

        # Compute the schedule
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        '''
            The function adds a new task to the scheduling, identifying the last available snapshot and 
            restoring the correct events lists.
        '''
        time = self.start
        count = 0

        # Here you can add the code to choose between different cores:
        new_task.core = self.cores[0].id
        # ------------------------------- #
        if new_task.type == 'sporadic' and new_task.activation > self.start:
            time = new_task.activation
            pos = search_pos(self, time - 1)

            # Restore the last snapshot that can be used to insert the new task
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(
                self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])

            # Add the new task and create the activation event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(
                new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1

            # Add the event inside the arrivals and sort them
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
                self.arrival_events_list[p].sort(key=lambda x: x.timestamp)

            self.arrival_events.append(copy.deepcopy(event))
            self.arrival_events.sort(key=lambda x: x.timestamp)
            time = self.time_list[pos] + 1
            delete(self, time)
        else:
            reset(self)
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1

        self.output_file.clean(time)
        self.compute(time, count)

    def add_time(self, add_time):
        '''
            Adds time to the simulation restoring the last available snapshot
            @param add_time the simulation time to be added at the end
        '''
        self.add_arrivals(self.end, self.end + add_time)

        # Restore the last available snapshot
        pos = search_pos(self, self.end - 1)
        self.finish_events = copy.deepcopy(self.finish_events_list[pos])
        self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
        self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
        self.start_events = copy.deepcopy(self.start_events_list[pos])
        self.executing = copy.deepcopy(self.executing_list[pos])
        self.end += add_time

        # Recompute with the new added time
        time = self.time_list[pos] + 1
        delete(self, time)
        self.output_file.clean(time)
        self.compute(time, self.start)

    def terminate(self):
        self.output_file.terminate_write()


class SJF(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'SJF'

    def compute(self, time, count):
        '''
            The function computes the scheduling actions starting from time and count
            @param time starting time
            @param count snapshot counter
        '''
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Sort by wcet (Shortest Job First)
            self.start_events.sort(key=lambda x: x.task.wcet)
            self.find_start_events(time)

            # Save the new snapshot if count = sqrt(size)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                self.finish_events_list.append(
                    copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(
                    copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(
                    copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                self.executing_list.append(copy.deepcopy(self.executing))
                count = 0
            time += 1

    def execute(self):
        '''
            The function executes the entire algorithm, preparing the number of snapshot size and the arrival events
        '''
        # Get all the events that need to be scheduled
        self.arrival_events = self.get_all_arrivals()

        # Set the number of steps to take a snapshot
        self.size = int(math.sqrt(self.end - self.start))

        # The first snapshot must be saved at time 0
        count = self.size - 1

        # Compute the schedule
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        '''
            The function adds a new task to the scheduling, identifying the last available snapshot and 
            restoring the correct events lists.
        '''
        time = self.start
        count = 0

        # Here you can add the code to choose between different cores:
        new_task.core = self.cores[0].id
        # ------------------------------- #
        if new_task.type == 'sporadic' and new_task.activation > self.start:
            time = new_task.activation
            pos = search_pos(self, time - 1)

            # Restore the last snapshot that can be used to insert the new task
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(
                self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])

            # Add the new task and create the activation event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(
                new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1

            # Add the event inside the arrivals and sort them
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
                self.arrival_events_list[p].sort(key=lambda x: x.timestamp)

            self.arrival_events.append(copy.deepcopy(event))
            self.arrival_events.sort(key=lambda x: x.timestamp)
            time = self.time_list[pos] + 1
            delete(self, time)
        else:
            reset(self)
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1

        self.output_file.clean(time)
        self.compute(time, count)

    def add_time(self, add_time):
        '''
            Adds time to the simulation restoring the last available snapshot
            @param add_time the simulation time to be added at the end
        '''
        self.add_arrivals(self.end, self.end + add_time)

        # Restore the last available snapshot
        pos = search_pos(self, self.end - 1)
        self.finish_events = copy.deepcopy(self.finish_events_list[pos])
        self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
        self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
        self.start_events = copy.deepcopy(self.start_events_list[pos])
        self.executing = copy.deepcopy(self.executing_list[pos])

        # Recompute with the new added time
        self.end += add_time
        time = self.time_list[pos] + 1
        delete(self, time)
        self.output_file.clean(time)
        self.compute(time, self.start)

    def terminate(self):
        self.output_file.terminate_write()


class HRRN(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'HRRN'

    def compute(self, time, count):
        '''
            The function computes the scheduling actions starting from time and count
            @param time starting time
            @param count snapshot counter
        '''
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Compute all the events response ratios
            self.calculate_responsive_ratio(time)
            # Sort by response ratio (Highest Response Ratio Next)
            self.start_events.sort(
                key=lambda x: x.response_ratio, reverse=True)
            self.find_start_events(time)

            # Save the new snapshot if count = sqrt(size)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                self.finish_events_list.append(
                    copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(
                    copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(
                    copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                self.executing_list.append(copy.deepcopy(self.executing))
                count = 0
            time += 1

    def execute(self):
        '''
            The function executes the entire algorithm, preparing the number of snapshot size and the arrival events
        '''
        # Get all the events that need to be scheduled
        self.arrival_events = self.get_all_arrivals()

        # Set the number of steps to take a snapshot
        self.size = int(math.sqrt(self.end - self.start))

        # The first snapshot must be saved at time 0
        count = self.size - 1

        # Compute the schedule
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        '''
            The function adds a new task to the scheduling, identifying the last available snapshot and 
            restoring the correct events lists.
        '''
        time = self.start
        count = 0

        # Here you can add the code to choose between different cores:
        new_task.core = self.cores[0].id
        # ------------------------------- #
        if new_task.type == 'sporadic' and new_task.activation > self.start:
            time = new_task.activation
            pos = search_pos(self, time - 1)

            # Restore the last snapshot that can be used to insert the new task
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(
                self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])

            # Add the new task and create the activation event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(
                new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1

            # Add the event inside the arrivals and sort them
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
                self.arrival_events_list[p].sort(key=lambda x: x.timestamp)

            self.arrival_events.append(copy.deepcopy(event))
            self.arrival_events.sort(key=lambda x: x.timestamp)
            time = self.time_list[pos] + 1
            delete(self, time)
        else:
            reset(self)
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1

        self.output_file.clean(time)
        self.compute(time, count)

    def calculate_responsive_ratio(self, time):
        '''
            The method computes all the responsive ratios for every event, in order to 
            sort them out during scheduling.
        '''
        for event in self.start_events:
            if event.init <= time:
                w = time - event.init
                c = event.task.wcet
                event.response_ratio = (w + c)/c

    def add_time(self, add_time):
        '''
            Adds time to the simulation restoring the last available snapshot
            @param add_time the simulation time to be added at the end
        '''
        self.add_arrivals(self.end, self.end + add_time)

        # Restore the last available snapshot
        pos = search_pos(self, self.end - 1)
        self.finish_events = copy.deepcopy(self.finish_events_list[pos])
        self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
        self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
        self.start_events = copy.deepcopy(self.start_events_list[pos])
        self.executing = copy.deepcopy(self.executing_list[pos])

        # Recompute with the new added time
        self.end += add_time
        time = self.time_list[pos] + 1
        delete(self, time)
        self.output_file.clean(time)
        self.compute(time, self.start)

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
        '''
            The method chooses what task to execute at the passed time. \n
            It evaluates the remaining time for every task and executes the one with lower remaining time.
            @param time current time
        '''
        if len(self.start_events) > 0:
            # Sort the events with respect to the remaining execution time
            self.start_events.sort(key=lambda x: x.remaining_time)

            # No task is executed
            if self.executing is None:
                # Add the first task to the executing one
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event
                self.create_deadline_event(event)

            # Change of task in case another one has a greater priority
            elif self.executing.remaining_time > self.start_events[0].remaining_time and \
                    self.executing.id != self.start_events[0].id:
                # Create finish event of the current task in execution
                finish_timestamp = time
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)

                # Change task
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event
                if event.task.first_time_executing:
                    self.create_deadline_event(event)

    def compute(self, time, count):
        '''
            The function computes the scheduling actions starting from time and count
            @param time starting time
            @param count snapshot counter
        '''
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Compute the updated remaining time for every task
            self.calculate_remaining_time()
            # Select the task to execute based on the remaining time (lower the best)
            self.choose_executed(time)
            if self.executing:
                self.executing.executing_time += 1

            # Save the new snapshot if count = sqrt(size)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                self.finish_events_list.append(
                    copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(
                    copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(
                    copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                self.executing_list.append(copy.deepcopy(self.executing))
                count = 0
            time += 1

    def execute(self):
        '''
            The function executes the entire algorithm, preparing the number of snapshot size and the arrival events
        '''
        # Get all the events that need to be scheduled
        self.arrival_events = self.get_all_arrivals()

        # Set the number of steps to take a snapshot
        self.size = int(math.sqrt(self.end - self.start))

        # The first snapshot must be saved at time 0
        count = self.size - 1

        # Compute the schedule
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        '''
            The function adds a new task to the scheduling, identifying the last available snapshot and 
            restoring the correct events lists.
        '''
        time = self.start
        count = 0

        # Here you can add the code to choose between different cores:
        new_task.core = self.cores[0].id
        # ------------------------------- #
        if new_task.type == 'sporadic' and new_task.activation > self.start:
            time = new_task.activation
            pos = search_pos(self, time - 1)

            # Restore the last snapshot that can be used to insert the new task
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(
                self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])

            if self.executing:
                self.executing = self.start_events[0]

            # Add the new task and create the activation event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(
                new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1

            # Add the event inside the arrivals and sort them
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
                self.arrival_events_list[p].sort(key=lambda x: x.timestamp)

            self.arrival_events.append(copy.deepcopy(event))
            self.arrival_events.sort(key=lambda x: x.timestamp)
            time = self.time_list[pos] + 1
            delete(self, time)
        else:
            reset(self)
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1

        self.output_file.clean(time)
        self.compute(time, count)

    def add_time(self, add_time):
        '''
            Adds time to the simulation restoring the last available snapshot
            @param add_time the simulation time to be added at the end
        '''
        self.add_arrivals(self.end, self.end + add_time)

        # Restore the last available snapshot
        pos = search_pos(self, self.end - 1)
        self.finish_events = copy.deepcopy(self.finish_events_list[pos])
        self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
        self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
        self.start_events = copy.deepcopy(self.start_events_list[pos])
        self.executing = copy.deepcopy(self.executing_list[pos])
        if self.executing:
            self.executing = self.start_events[0]

        # Recompute with the new added time
        self.end += add_time
        time = self.time_list[pos] + 1
        delete(self, time)
        self.output_file.clean(time)
        self.compute(time, self.start)

    def terminate(self):
        self.output_file.terminate_write()


class RoundRobin(Preemptive):

    def __init__(self, output_file, quantum):
        super().__init__(output_file)
        self.name = 'RoundRobin'
        self.quantum = int(quantum)
        self.quantum_counter = 0

    def choose_executed(self, time):
        '''
            The method chooses what task to execute at the passed time. \n
            It evaluates the quantum counter every task and executes the next one when the quantum counter is\n
            equal to the quantum dimension set when the object is created.
            @param time current time
        '''
        if len(self.start_events) > 0:
            # No task is executed
            if self.executing is None:
                # Add the first task to the executing one
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event

                # Create deadline event
                self.create_deadline_event(event)
                # Restart quantum counter
                self.quantum_counter = 0

            # Change of task
            elif self.quantum_counter == self.quantum:
                # Create finish event of the current task in execution
                finish_timestamp = time
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)

                # Change task:
                # 1) Delete from start_events
                del self.start_events[0]
                # 2) Add this event to the final
                self.start_events.append(copy.deepcopy(self.executing))
                # 3) New event
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event

                # Create deadline event
                if event.task.first_time_executing:
                    self.create_deadline_event(event)
                # Restart counter
                self.quantum_counter = 0

    def compute(self, time, count):
        '''
            The function computes the scheduling actions starting from time and count
            @param time starting time
            @param count snapshot counter
        '''
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Select the next task to execute based on the quantum counter
            self.choose_executed(time)
            self.quantum_counter += 1
            if self.executing:
                self.executing.executing_time += 1

            # Save the new snapshot if count = sqrt(size)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                self.finish_events_list.append(
                    copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(
                    copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(
                    copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                self.executing_list.append(copy.deepcopy(self.executing))
                self.quantum_counter_list.append(self.quantum_counter)
                count = 0
            time += 1

    def execute(self):
        '''
            The function executes the entire algorithm, preparing the number of snapshot size and the arrival events
        '''
        # Get all the events that need to be scheduled
        self.arrival_events = self.get_all_arrivals()

        # Set the number of steps to take a snapshot
        self.size = int(math.sqrt(self.end - self.start))

        # The first snapshot must be saved at time 0
        count = self.size - 1

        # Compute the schedule
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        '''
            The function adds a new task to the scheduling, identifying the last available snapshot and 
            restoring the correct events lists.
        '''
        time = self.start
        count = 0

        # Here you can add the code to choose between different cores:
        new_task.core = self.cores[0].id
        # ------------------------------- #
        if new_task.type == 'sporadic' and new_task.activation > self.start:
            time = new_task.activation
            pos = search_pos(self, time - 1)

            # Restore the last snapshot that can be used to insert the new task
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(
                self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])
            self.quantum_counter = self.quantum_counter_list[pos]

            if self.executing:
                self.executing = self.start_events[0]

            # Add the new task and create the activation event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(
                new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1

            # Add the event inside the arrivals and sort them
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
                self.arrival_events_list[p].sort(key=lambda x: x.timestamp)

            self.arrival_events.append(copy.deepcopy(event))
            self.arrival_events.sort(key=lambda x: x.timestamp)
            time = self.time_list[pos] + 1
            delete(self, time)
        else:
            reset(self)
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1

        self.output_file.clean(time)
        self.compute(time, count)

    def add_time(self, add_time):
        '''
            Adds time to the simulation restoring the last available snapshot
            @param add_time the simulation time to be added at the end
        '''
        self.add_arrivals(self.end, self.end + add_time)

        # Restore the last available snapshot
        pos = search_pos(self, self.end - 1)
        self.finish_events = copy.deepcopy(self.finish_events_list[pos])
        self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
        self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
        self.start_events = copy.deepcopy(self.start_events_list[pos])
        self.executing = copy.deepcopy(self.executing_list[pos])
        self.quantum_counter = self.quantum_counter_list[pos]
        if self.executing:
            self.executing = self.start_events[0]

        # Recompute with the new added time
        self.end += add_time
        time = self.time_list[pos] + 1
        delete(self, time)
        self.output_file.clean(time)
        self.compute(time, self.start)

    def terminate(self):
        self.output_file.terminate_write()


class RateMonotonic(Preemptive):
    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'RateMonotonic'

    def choose_executed(self, time):
        '''
            The method chooses what task to execute at the passed time. \n
            It evaluates the period of every task and executes the task based on its priority (shorter period = high priority)
            @param time current time
        '''
        if len(self.start_events) > 0:
            # No task is executed
            if self.executing is None:
                # Add the first task to the executing one
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event

                # Create deadline event
                self.create_deadline_event(event)

            # Change of task if another one has a higher priority (aka a smaller period)
            elif self.executing.period > self.start_events[0].period and self.executing.id != self.start_events[0].id:
                # Create finish event of the current task in execution
                finish_timestamp = time
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, self.executing.task, SchedEvent.EventType.finish.value, self.executing.id)
                finish_event.job = self.executing.job
                self.output_file.add_scheduler_event(finish_event)

                # Change task
                event = self.start_events[0]
                event.timestamp = time
                self.output_file.add_scheduler_event(event)
                self.executing = event
                # Create deadline event
                if event.task.first_time_executing:
                    self.create_deadline_event(event)

    def compute(self, time, count):
        '''
            The function computes the scheduling actions starting from time and count
            @param time starting time
            @param count snapshot counter
        '''
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Select the next task to execute based on the priority
            self.choose_executed(time)
            if self.executing:
                self.executing.executing_time += 1

            # Save the new snapshot if count = sqrt(size)
            count += 1
            if count == self.size:
                self.time_list.append(time)
                self.finish_events_list.append(
                    copy.deepcopy(self.finish_events))
                self.deadline_events_list.append(
                    copy.deepcopy(self.deadline_events))
                self.arrival_events_list.append(
                    copy.deepcopy(self.arrival_events))
                self.start_events_list.append(copy.deepcopy(self.start_events))
                self.executing_list.append(copy.deepcopy(self.executing))
                count = 0
            time += 1

    def execute(self):
        '''
            The function executes the entire algorithm, preparing the number of snapshot size and the arrival events
        '''
        # Get all the events that need to be scheduled
        self.arrival_events = self.get_all_arrivals()

        # Set the number of steps to take a snapshot
        self.size = int(math.sqrt(self.end - self.start))

        # The first snapshot must be saved at time 0
        count = self.size - 1

        # Compute the schedule
        time = self.start
        self.compute(time, count)

    def new_task(self, new_task):
        '''
            The function adds a new task to the scheduling, identifying the last available snapshot and 
            restoring the correct events lists.
        '''
        time = self.start
        count = 0

        # Here you can add the code to choose between different cores:
        new_task.core = self.cores[0].id
        # ------------------------------- #
        if new_task.type == 'sporadic' and new_task.activation > self.start:
            time = new_task.activation
            pos = search_pos(self, time - 1)

            # Restore the last snapshot that can be used to insert the new task
            self.finish_events = copy.deepcopy(self.finish_events_list[pos])
            self.deadline_events = copy.deepcopy(
                self.deadline_events_list[pos])
            self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
            self.start_events = copy.deepcopy(self.start_events_list[pos])
            self.executing = copy.deepcopy(self.executing_list[pos])

            if self.executing:
                self.executing = self.start_events[0]

            # Add the new task and create the activation event
            self.tasks.append(new_task)
            new_task.init = new_task.activation
            event = SchedEvent.ScheduleEvent(
                new_task.activation, new_task, SchedEvent.EventType.activation.value, self.event_id)
            self.event_id += 1

            # Add the event inside the arrivals and sort them
            for p in range(pos + 1):
                self.arrival_events_list[p].append(copy.deepcopy(event))
                self.arrival_events_list[p].sort(key=lambda x: x.timestamp)

            self.arrival_events.append(copy.deepcopy(event))
            self.arrival_events.sort(key=lambda x: x.timestamp)
            time = self.time_list[pos] + 1
            delete(self, time)
        else:
            reset(self)
            self.tasks.append(new_task)
            self.arrival_events = self.get_all_arrivals()
            count = self.size - 1

        self.output_file.clean(time)
        self.compute(time, count)

    def add_time(self, add_time):
        '''
            Adds time to the simulation restoring the last available snapshot
            @param add_time the simulation time to be added at the end
        '''
        self.add_arrivals(self.end, self.end + add_time)

        # Restore the last available snapshot
        pos = search_pos(self, self.end - 1)
        self.finish_events = copy.deepcopy(self.finish_events_list[pos])
        self.deadline_events = copy.deepcopy(self.deadline_events_list[pos])
        self.arrival_events = copy.deepcopy(self.arrival_events_list[pos])
        self.start_events = copy.deepcopy(self.start_events_list[pos])
        self.executing = copy.deepcopy(self.executing_list[pos])
        if self.executing:
            self.executing = self.start_events[0]

        # Recompute with the new added time
        self.end += add_time
        time = self.time_list[pos] + 1
        delete(self, time)
        self.output_file.clean(time)
        self.compute(time, self.start)

    def terminate(self):
        self.output_file.terminate_write()
