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
        self.events = []

    @abstractmethod
    def compute_and_add(self, time: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]):
        '''
            The method allows the server scheduler to modify the start/arrival events depending on the scheduling policy.
            If just a "periodic" start event has to be added, then this method does so. 
            If the arrival events priorities have to be modified, then it can do it.\n
            THIS IS A MODIFIER METHOD, start_events and arrival_events MUST BE CONSIDERED MUTED.
        '''
        pass

    def add_arrival_event(self, event: SchedEvent.ScheduleEvent):
        if event not in self.events:
            self.events.append(event)


class PollingServer(ServerScheduler):
    def __init__(self, capacity, period) -> None:
        super().__init__()
        self.name = "Polling"
        self.capacity = capacity
        self.period = period

    def compute_and_add(self, time: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]):
        # Restore total capacity in case the period has passed
        if time == 1 or time % self.period == 0:
            self.runtime_capacity = self.capacity

        # Events with an earlier activation get scheduled first
        self.events.sort(key=lambda x: x.task.activation)

        # Add events such that the overall capacity is met
        while len(self.events) > 0 and self.runtime_capacity > 0:
            # Add the start event into the list
            start_event = SchedEvent.ScheduleEvent(
                self.events[0].task.activation, self.events[0].task, SchedEvent.EventType.start.value, self.events[0].id)
            start_event.job = self.events[0].job

            # The servers gives its priority to the async task
            start_event.period = self.period

            # Add the event to the start list to be scheduled
            start_events.append(start_event)

            # TODO: Check that the wcet of the task may be greater than the server capacity
            self.runtime_capacity -= self.events[0].task.wcet

            # Remove the processed value from the
            self.events.remove(self.events[0])

        # At the end reset the capacity until the next period arrives
        self.runtime_capacity = 0

class DeferrableServer(ServerScheduler):
    def __init__(self, capacity, period) -> None:
        super().__init__()
        self.name = "Deferrable"
        self.capacity = capacity
        self.period = period
    
    def compute_and_add(self, time, start_events, arrival_events):
        # Restore total capacity in case the period has passed
        if time == 1 or time % self.period == 0:
            self.runtime_capacity = self.capacity

        # Events with an earlier activation get scheduled first
        self.events.sort(key=lambda x: x.task.activation)

        # Add events such that the overall capacity is met
        while len(self.events) > 0 and self.runtime_capacity > 0:
            # Add the start event into the list
            start_event = SchedEvent.ScheduleEvent(
                self.events[0].task.activation, self.events[0].task, SchedEvent.EventType.start.value, self.events[0].id)
            start_event.job = self.events[0].job

            # The servers gives its priority to the async task
            start_event.period = self.period

            # Add the event to the start list to be scheduled
            start_events.append(start_event)

            # TODO: Check that the wcet of the task may be greater than the server capacity
            self.runtime_capacity -= self.events[0].task.wcet

            # Remove the processed value from the
            self.events.remove(self.events[0])

class PriorityExchangeServer(ServerScheduler):
    def __init__(self, capacity, period) -> None:
        super().__init__()
        self.name = "PriorityExchange"
        self.capacity = capacity
        self.period = period
        self.runtime_capacity = []

    def compute_and_add(self, time, start_events, arrival_events):
        # Add the capacity at multiples of the period
        if time == 1 or time % self.period == 0:
            # Append the new server capacity at its original priority (server period)
            for i in range(self.capacity):
                self.runtime_capacity.append(self.period)

        # Priority Exchange
        if len(self.events) == 0:
            pass