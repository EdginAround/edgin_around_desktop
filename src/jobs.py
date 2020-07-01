from typing import Optional


class Job:
    def __init__(self) -> None:
        pass

    def get_repeat_delay(self) -> Optional[float]:
        return None


class HungerDrainJob(Job):
    def __init__(self) -> None:
        super().__init__()

    def get_repeat_delay(self) -> float:
        return 1.0

