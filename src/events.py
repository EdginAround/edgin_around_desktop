from typing import List, Optional

from . import defs


class Event(defs.Debugable):
    DEBUG_FIELDS: List[str] = []

    def __init__(self, receiver_id) -> None:
        self._receiver_id = receiver_id

    def get_receiver_id(self) -> defs.ActorId:
        return self._receiver_id


class ResumeEvent(Event):
    def __init__(self, receiver_id: defs.ActorId) -> None:
        super().__init__(receiver_id)


class FinishedEvent(Event):
    def __init__(self, receiver_id: defs.ActorId) -> None:
        super().__init__(receiver_id)


class StopEvent(Event):
    def __init__(self, receiver_id: defs.ActorId) -> None:
        super().__init__(receiver_id)


class ConcludeEvent(Event):
    def __init__(self, receiver_id: defs.ActorId) -> None:
        super().__init__(receiver_id)


class StartMovingEvent(Event):
    DEBUG_FIELDS = ['bearing']

    def __init__(self, receiver_id: defs.ActorId, bearing) -> None:
        super().__init__(receiver_id)
        self.bearing = bearing


class HandActivationEvent(Event):
    DEBUG_FIELDS = ['hand', 'object_id']

    def __init__(
            self,
            receiver_id: defs.ActorId,
            hand: defs.Hand,
            object_id: Optional[defs.ActorId],
        ) -> None:
        super().__init__(receiver_id)
        self.hand = hand
        self.object_id = object_id


class InventorySwapEvent(Event):
    DEBUG_FIELDS = ['hand', 'inventory_index']

    def __init__(
            self,
            receiver_id: defs.ActorId,
            hand: defs.Hand,
            inventory_index: int,
        ) -> None:
        super().__init__(receiver_id)
        self.hand = hand
        self.inventory_index = inventory_index


class DamageEvent(Event):
    DEBUG_FIELDS = ['dealer_id', 'receiver_id', 'damage_amount', 'damage_variant']

    def __init__(
            self,
            receiver_id: defs.ActorId,
            dealer_id: defs.ActorId,
            damage_amount: float,
            damage_variant: defs.DamageVariant,
        ) -> None:
        super().__init__(receiver_id)
        self.dealer_id = dealer_id
        self.receiver_id = receiver_id
        self.damage_amount = damage_amount
        self.damage_variant = damage_variant

