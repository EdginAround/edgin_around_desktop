import time

from typing import List, Optional

from . import actions, defs, essentials, features, events, jobs, scene, state


class MovementTask(essentials.Task):
    TIMEOUT = 20.0 # seconds

    def __init__(self, entity_id: defs.ActorId, speed: float, bearing: float) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.speed = speed
        self.bearing = bearing
        self.job = jobs.MovementJob(entity_id, self.speed, self.bearing, self.TIMEOUT, list())

    def start(self, state: state.State) -> List[actions.Action]:
        return [actions.MovementAction(self.entity_id, self.speed, self.bearing, self.TIMEOUT)]

    def get_job(self) -> Optional[essentials.Job]:
        return self.job

    def finish(self, state: state.State) -> List[actions.Action]:
        assert self.job is not None

        entity = state.get_entity(self.entity_id)
        assert entity is not None

        interval = time.monotonic() - self.job.get_prev_call_time()
        entity.move_by(self.speed * interval, self.bearing, state.get_radius())

        position = entity.get_position()
        assert position is not None
        return [actions.LocalizeAction(self.entity_id, position)]


class WalkTask(essentials.Task):
    def __init__(
            self,
            entity_id: defs.ActorId,
            speed: float,
            bearing: float,
            duration: float,
        ) -> None:
        super().__init__()
        self.entity_id = entity_id
        self.speed = speed
        self.bearing = bearing
        self.duration = duration

    def start(self, state: state.State) -> List[actions.Action]:
        return [actions.MovementAction(self.entity_id, self.speed, self.bearing, self.duration)]

    def get_job(self) -> Optional[essentials.Job]:
        return jobs.MovementJob(
                self.entity_id,
                self.speed,
                self.bearing,
                self.duration,
                [events.FinishedEvent(self.entity_id)],
            )

    def finish(self, state: state.State) -> List[actions.Action]:
        entity = state.get_entity(self.entity_id)
        assert entity is not None
        position = entity.get_position()
        assert position is not None
        return [actions.LocalizeAction(self.entity_id, position)]


class PickItemTask(essentials.Task):
    PICK_DURATION = 1.0 # sec
    MAX_DISTANCE = 1.0

    def __init__(
            self,
            who_id: essentials.EntityId,
            what_id: Optional[essentials.EntityId],
            hand: defs.Hand,
        ) -> None:
        super().__init__()
        self.who_id = who_id
        self.what_id = what_id
        self.hand = hand
        self.job: Optional[essentials.Job] = None

    def start(self, state: state.State) -> List[actions.Action]:
        if self.what_id is None:
            self.what_id = state.find_closest_delivering_within \
                (self.who_id, [features.Claim.CARGO], self.MAX_DISTANCE)

        if self.what_id is None:
            return list()

        entity = state.get_entity(self.who_id)
        item = state.get_entity(self.what_id)
        if entity is None or item is None:
            return list()

        distance = state.calculate_distance(entity, item)
        if distance is None or self.MAX_DISTANCE < distance:
            return list()

        if self.what_id is not None:
            self.job = jobs.WaitJob(self.PICK_DURATION, [events.FinishedEvent(self.who_id)])
            return [actions.PickStartAction(self.who_id, self.what_id)]
        else:
            return list()

    def get_job(self) -> Optional[essentials.Job]:
        return self.job

    def finish(self, state: state.State) -> List[actions.Action]:
        if self.what_id is None:
            return list()

        entity = state.get_entity(self.who_id)
        item = state.get_entity(self.what_id)
        if entity is None or item is None:
            return list()

        if not entity.features.inventory or not item.features.inventorable:
            return list()

        distance = state.calculate_distance(entity, item)
        if distance is None or self.MAX_DISTANCE < distance:
            return list()

        entity.features.inventory.store(self.hand, item.get_id(), item.get_name())
        item.features.inventorable.set_stored_by(entity.get_id())
        item.set_position(None)

        result = [
                actions.PickEndAction(self.who_id),
                actions.UpdateInventoryAction(entity.features.inventory.get()),
            ]

        if self.what_id is not None:
            result.append(actions.DeleteActorsAction([self.what_id]))

        return result


class UseItemTask(essentials.Task):
    MAX_DISTANCE = 1.0

    def __init__(
            self,
            performer_id: essentials.EntityId,
            item_id: essentials.EntityId,
            receiver_id: Optional[essentials.EntityId],
        ) -> None:
        super().__init__()
        self.performer_id = performer_id
        self.item_id = item_id
        self.receiver_id = receiver_id
        self.job: Optional[essentials.Job] = None

    def start(self, state: state.State) -> List[actions.Action]:
        performer = state.get_entity(self.performer_id)
        item = state.get_entity(self.item_id)
        if performer is None or item is None:
            return list()

        claims = item.features.delivery_claims()

        self.receiver_id = self.receiver_id if self.receiver_id else \
            state.find_closest_absorbing_within(self.performer_id, claims, self.MAX_DISTANCE)

        if self.receiver_id is None:
            return list()

        receiver = state.get_entity(self.receiver_id)
        if receiver is None:
            return list()

        distance = state.calculate_distance(performer, receiver)
        if distance is None or self.MAX_DISTANCE < distance:
            return list()

        claim = receiver.features.get_first_absorbed(claims)

        if claim is None:
            pass

        elif claim is features.Claim.PAIN:
            self.job = jobs.DamageJob(
                    self.performer_id,
                    self.receiver_id,
                    self.item_id,
                    [events.FinishedEvent(self.performer_id)],
                )

        elif claim is features.Claim.FOOD:
            # TODO: Implement eating items.
            pass

        elif claim is features.Claim.CARGO:
            # TODO: Implement giving items.
            pass

        else:
            defs.assert_exhaustive(claim)

        return list()

    def get_job(self) -> Optional[essentials.Job]:
        return self.job

    def finish(self, state: state.State) -> List[actions.Action]:
        return list()


class DieAndDrop(essentials.Task):
    DIE_DURATION = 0.01 # sec

    def __init__(
            self,
            dier_id: essentials.EntityId,
            drops: List[essentials.Entity]
        ) -> None:
        super().__init__()
        self.dier_id = dier_id
        self.drops = drops
        self.job = jobs.WaitJob(self.DIE_DURATION, [events.FinishedEvent(self.dier_id)])

    def start(self, state: state.State) -> List[actions.Action]:
        dier = state.get_entity(self.dier_id)
        if dier is None:
            return list()

        for drop in self.drops:
            state.add_entity(drop)

        drops = [scene.Actor(
                drop.id, drop.position, drop.get_name(),
            ) for drop in self.drops]

        return [
                actions.CreateActorsAction(drops),
                actions.DeleteActorsAction([self.dier_id])
            ]

    def get_job(self) -> Optional[essentials.Job]:
        return self.job

    def finish(self, state: state.State) -> List[actions.Action]:
        return list()

