from . import defs


class Event:
    def __init__(self) -> None:
        pass


class ResumeEvent(Event):
    def __init__(self) -> None:
        super().__init__()

    def __eq__(self, other):
        return self.__class__ == other.__class__


class FinishedEvent(Event):
    def __init__(self) -> None:
        super().__init__()

    def __eq__(self, other):
        return self.__class__ == other.__class__


class StartMovingEvent(Event):
    def __init__(self, bearing) -> None:
        super().__init__()
        self.bearing = bearing

    def __eq__(self, other):
        return self.__class__ == other.__class__


class StopMovingEvent(Event):
    def __init__(self) -> None:
        super().__init__()

    def __eq__(self, other):
        return self.__class__ == other.__class__


class HandActivationEvent(Event):
    def __init__(self, hand: defs.Hand, item_id: defs.ActorId) -> None:
        super().__init__()
        self.hand = hand
        self.item_id = item_id

    def __eq__(self, other):
        return self.__class__ == other.__class__

