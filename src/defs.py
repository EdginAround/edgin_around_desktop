from enum import Enum


ActorId = int


class Hand(Enum):
    LEFT = 0
    RIGHT = 1


class Stats:
    def __init__(self, hunger, max_hunger) -> None:
        self.hunger = hunger
        self.max_hunger = max_hunger

