import abc, json, time

from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING

import edgin_around_rendering as ear
from edgin_around_api import actions, defs, geometry, inventory
from . import thrusting

# TODO: Move constants to the API module.
MAX_PICK_DISTANCE = 1.0


class MotiveName:
    IDLE = "idle"
    WALK = "walk"
    PICK = "pick"
    DAMAGED = "damaged"
    SWING_LEFT = "swing_left"
    SWING_RIGHT = "swing_right"


class Motive(abc.ABC):
    def __init__(self, timeout):
        self._expired = False
        self.start_time = time.monotonic()
        self.timeout = timeout

    def expired(self) -> bool:
        if self._expired:
            return True

        elif self.timeout is not None:
            return self.start_time + self.timeout < time.monotonic()

        else:
            return False

    # If a newly added action returns an actor ID, it cancels and replaces any other action assigned
    # to the same actor.
    def get_actor_id(self) -> Optional[defs.ActorId]:
        return None

    def expire(self) -> None:
        self._expired = True

    @abc.abstractmethod
    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        raise NotImplementedError("This motive is not implemented")

    def refresh_highlight(self, context: thrusting.MotiveContext) -> None:
        hero_id = context.scene.get_hero_id()
        hero_position = context.scene.get_actor_position(hero_id)
        if hero_position is None:
            return

        actors = context.scene.find_closest_actors(hero_position, MAX_PICK_DISTANCE)
        # The hero will always be the closest actor
        if len(actors) > 1:
            context.world.set_highlighted_actor_id(actors[1])
        else:
            context.world.remove_highlight()


class ConfigurationMotive(Motive):
    def __init__(self, action: actions.ConfigurationAction) -> None:
        super().__init__(None)
        self.hero_actor_id = action.hero_actor_id
        self.elevation = action.elevation

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        elevation = ear.ElevationFunction(self.elevation.radius)
        for terrain in self.elevation.terrain:
            origin = terrain.get_origin()
            elevation.add_terrain(terrain.get_name(), origin.theta, origin.phi)

        context.scene.configure(self.hero_actor_id, elevation)
        self.expire()


class CraftStartMotive(Motive):
    def __init__(self, action: actions.CraftStartAction) -> None:
        super().__init__(None)
        self.crafter_id = action.crafter_id

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        self.expire()


class CraftEndMotive(Motive):
    def __init__(self, action: actions.CraftEndAction) -> None:
        super().__init__(None)
        self.crafter_id = action.crafter_id

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        self.expire()


class CreateActorsMotive(Motive):
    def __init__(self, action: actions.CreateActorsAction) -> None:
        super().__init__(None)
        self.actors = action.actors

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        actors = list()
        for a in self.actors:
            position: Optional[ear.Point]
            if a.position is not None:
                position = ear.Point(a.position.theta, a.position.phi)
            else:
                position = None

            actors.append(ear.Actor(a.id, a.entity_name, position))

        context.scene.create_actors(actors)
        context.world.create_renderers(actors)
        self.refresh_highlight(context)
        self.expire()


class DeleteActorsMotive(Motive):
    def __init__(self, action: actions.DeleteActorsAction) -> None:
        super().__init__(None)
        self.actor_ids = action.actor_ids

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        context.scene.delete_actors(self.actor_ids)
        context.world.delete_renderers(self.actor_ids)
        self.refresh_highlight(context)
        self.expire()


class MovementMotive(Motive):
    def __init__(self, action: actions.MovementAction) -> None:
        super().__init__(action.duration)
        self.actor_id = action.actor_id
        self.speed = action.speed
        self.bearing = action.bearing
        self._tick_count = 0

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        distance = self.speed * interval

        old_position = context.scene.get_actor_position(self.actor_id)
        if old_position is None:
            return

        old_point = geometry.Point(old_position.get_theta(), old_position.get_phi())
        new_point = old_point.moved_by(distance, self.bearing, context.scene.get_radius())
        new_position = ear.Point(new_point.theta, new_point.phi)
        context.scene.set_actor_position(self.actor_id, new_position)

        if self._tick_count == 0:
            context.world.play_animation(self.actor_id, MotiveName.WALK)

        self.refresh_highlight(context)
        self._tick_count += 1


class LocalizeMotive(Motive):
    def __init__(self, action: actions.LocalizeAction) -> None:
        super().__init__(None)
        self.actor_id = action.actor_id
        self.position = action.position

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        position = ear.Point(self.position.theta, self.position.phi)
        context.scene.set_actor_position(self.actor_id, position)
        context.world.play_animation(self.actor_id, MotiveName.IDLE)
        self.refresh_highlight(context)
        self.expire()


class StatUpdateMotive(Motive):
    def __init__(self, action: actions.StatUpdateAction) -> None:
        super().__init__(None)
        self.actor_id = action.actor_id
        self.stats = action.stats

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        context.gui.set_stats(self.stats)
        self.expire()


class PickStartMotive(Motive):
    def __init__(self, action: actions.PickStartAction) -> None:
        super().__init__(None)
        self.actor_id = action.who
        self.item_id = action.what

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        context.world.play_animation(self.actor_id, MotiveName.PICK)
        self.expire()


class PickEndMotive(Motive):
    def __init__(self, action: actions.PickEndAction) -> None:
        super().__init__(None)
        self.actor_id = action.who

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        context.world.play_animation(self.actor_id, MotiveName.IDLE)
        self.expire()


class UpdateInventoryMotive(Motive):
    def __init__(self, action: actions.UpdateInventoryAction) -> None:
        super().__init__(None)
        self.owner_id = action.owner_id
        self.inventory = action.inventory

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        context.gui.set_inventory(self.inventory)

        context.scene.hide_actors(self.inventory.get_all_ids())

        left_item = self.inventory.get_hand(defs.Hand.LEFT)
        context.world.attach_actor(defs.Attachement.LEFT_ITEM.value, self.owner_id, left_item)

        right_item = self.inventory.get_hand(defs.Hand.RIGHT)
        context.world.attach_actor(defs.Attachement.RIGHT_ITEM.value, self.owner_id, right_item)

        self.expire()


class DamageMotive(Motive):
    def __init__(self, action: actions.DamageAction) -> None:
        super().__init__(None)
        self.dealer_id = action.dealer_id
        self.receiver_id = action.receiver_id
        self.variant = action.variant
        self.hand = action.hand

    def tick(self, interval, context: thrusting.MotiveContext) -> None:
        if self.hand == defs.Hand.LEFT:
            context.world.play_animation(self.dealer_id, MotiveName.SWING_LEFT)
        else:
            context.world.play_animation(self.dealer_id, MotiveName.SWING_RIGHT)
        context.world.play_animation(self.receiver_id, MotiveName.DAMAGED)

        # Play sounds
        context.sounds.play(self.variant.value)

        # Remove the animation
        self.expire()


_ANIMATION_CONSTRUCTORS: Dict[type, Any] = {
    actions.ConfigurationAction: ConfigurationMotive,
    actions.CraftStartAction: CraftStartMotive,
    actions.CraftEndAction: CraftEndMotive,
    actions.CreateActorsAction: CreateActorsMotive,
    actions.DeleteActorsAction: DeleteActorsMotive,
    actions.MovementAction: MovementMotive,
    actions.LocalizeAction: LocalizeMotive,
    actions.StatUpdateAction: StatUpdateMotive,
    actions.PickStartAction: PickStartMotive,
    actions.PickEndAction: PickEndMotive,
    actions.UpdateInventoryAction: UpdateInventoryMotive,
    actions.DamageAction: DamageMotive,
}


def motive_from_action(action: actions.Action) -> Optional[Motive]:
    """Converts an `Action` into a `Motive`."""

    return _ANIMATION_CONSTRUCTORS[type(action)](action)
