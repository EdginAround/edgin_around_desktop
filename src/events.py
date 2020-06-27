class Event:
    def __init__(self) -> None:
        pass


class ConnectionEvent(Event):
    def __init__(self) -> None:
        super().__init__()


class ResumeEvent(Event):
    def __init__(self) -> None:
        super().__init__()


class FinishedEvent(Event):
    def __init__(self) -> None:
        super().__init__()

