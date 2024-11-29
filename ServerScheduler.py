from abc import abstractmethod

from SchedEvent import ScheduleEvent
import SchedEvent
import Task


class ServerScheduler:
    def __init__(self) -> None:
        self.name = "ServerScheduler"
        self.capacity = 0
        self.runtime_capacity = 0
        self.period = 0
        self.tasks = []
        self.id = 0

    @abstractmethod
    def compute_and_add(self, time: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]) -> int:
        '''
            The method allows the server scheduler to modify the start/arrival events depending on the scheduling policy.
            If just a "periodic" start event has to be added, then this method does so. 
            If the arrival events priorities have to be modified, then it can do it.\n
            THIS IS MODIFIER METHOD, start_events and arrival_events MUST BE CONSIDERED MUTED.\n
            Returns the new event_id for the scheduler.
        '''
        pass

    def add_task(self, task: Task.Task):
        if task not in self.tasks:
            self.tasks.append(task)

            # Update the internal ID to use the minimum listed on the added tasks
            if self.id == 0 or self.id > task.id:
                self.id = task.id


class PollingServer(ServerScheduler):
    def __init__(self, capacity, period) -> None:
        super().__init__()
        self.name = "Polling"
        self.capacity = capacity
        self.period = period

    def compute_and_add(self, time: int, event_id: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]) -> int:
        # Restore total capacity in case the period has passed
        if time == 1 or time % self.period == 0:
            self.runtime_capacity = self.capacity

        # Tasks with an earlier activation get scheduled first
        self.tasks.sort(key=lambda x: x.activation)

        # Add tasks such that the overall capacity is met
        while len(self.tasks) > 0 and self.runtime_capacity > 0 and self.tasks[0].activation <= time:
            # TODO: Add the multiple cores here if needed
            self.tasks[0].core = 0
            self.tasks[0].id = self.id

            # Add the start event into the list
            start_event = SchedEvent.ScheduleEvent(
                self.tasks[0].activation, self.tasks[0], SchedEvent.EventType.start.value, event_id)
            event_id += 1

            # The servers gives its priority to the async task
            start_event.period = self.period

            # Add the event to the start list to be scheduled
            start_events.append(start_event)

            # TODO: Check that the wcet of the task may be greater than the server capacity
            self.runtime_capacity -= self.tasks[0].wcet

            # Remove the processed value from the
            self.tasks.remove(self.tasks[0])

        # At the end reset the capacity until the next period arrives
        self.runtime_capacity = 0

        return event_id
