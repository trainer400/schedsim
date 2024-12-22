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


class PriorityExchangeServer(ServerScheduler):
    def __init__(self, capacity, period) -> None:
        super().__init__()
        self.name = "PriorityExchange"
        self.capacity = capacity
        self.period = period
        self.runtime_capacity = []

    def compute_and_add(self, time: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]):
        # Add the capacity at multiples of the period
        if time % self.period == 0:
            # Append the new server capacity at its original priority (server period)
            for i in range(self.capacity):
                self.runtime_capacity.append(self.period)

        # Act with priority exchanges only if there are still tasks that can support change of priorities
        if len(start_events) > 0:
            # Sort the start events with respect to the period (TODO: Remove Rate Monotonic assumption)
            start_events.sort(key=lambda x: x.period)
            next_event = start_events[0]

            # Priority Exchange if the server has the highest priority (TODO: Remove Rate Monotonic assumption)
            if len(self.events) == 0 and self.period < next_event.period and next_event.task.type != "sporadic":
                # For every runtime capacity point, if it is greater, change it to the next task priority
                for i in range(len(self.runtime_capacity)):
                    if self.runtime_capacity[i] < next_event.period:
                        self.runtime_capacity[i] = next_event.period

                # TODO: Define if this instruction is needed
                # next_event.period = self.period

        # Sort the runtime capacity such that the lower period (aka. highest priority) tokens are the first
        self.runtime_capacity.sort(key=lambda x: x)

        # Schedule the aperiodic tasks with the cumulated runtime capacity
        if len(self.events) > 0:
            self.events.sort(key=lambda x: x.timestamp)
            next_event = self.events[0]

            # Schedule the event only if there is enough capacity
            if len(self.runtime_capacity) > next_event.task.wcet:
                # Because the capacity priority can change within the same task
                # we create a different start event for each priority change
                previous_priority = -1
                start_event = None
                for i in range(next_event.task.wcet):
                    if self.runtime_capacity[i] != previous_priority:
                        # Register the so far created start_event
                        if start_event != None:
                            start_events.append(start_event)

                        previous_priority = self.runtime_capacity[i]

                        # Add the start event into the list
                        start_event = SchedEvent.ScheduleEvent(
                            next_event.task.activation, next_event.task, SchedEvent.EventType.start.value, next_event.id)
                        start_event.job = next_event.job

                        # The servers gives its priority to the async task
                        start_event.period = self.runtime_capacity[i]
                        start_event.task.wcet = 1
                    else:
                        start_event.task.wcet += 1

                # Append the final event
                start_events.append(start_event)

                # Remove the first N (wcet) runtime capacity
                for i in range(next_event.task.wcet):
                    self.runtime_capacity.remove(self.runtime_capacity[0])

                # Remove the just scheduled event
                self.events.remove(next_event)
