from abc import abstractmethod

from SchedEvent import ScheduleEvent


class ServerScheduler:
    def __init__(self) -> None:
        self.name = "ServerScheduler"
        self.capacity = 0
        self.period = 0
        self.tasks = []

    @abstractmethod
    def compute_and_add(time: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]):
        '''
            The method allows the server scheduler to modify the start/arrival events depending on the scheduling policy.
            If just a "periodic" start event has to be added, then this method does so. 
            If the arrival events priorities have to be modified, then it can do it.\n
            THIS IS MODIFIER METHOD, start_events and arrival_events MUST BE CONSIDERED MUTED
        '''
        pass


class PollingServer(ServerScheduler):
    def __init__(self, capacity, period) -> None:
        super().__init__()
        self.name = "Polling"
        self.capacity = capacity
        self.period = period

    def compute_and_add(time: int, start_events: list[ScheduleEvent], arrival_events: list[ScheduleEvent]):
        pass
