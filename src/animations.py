import abc, json, time

from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING

import edgin_around_rendering as ear
from edgin_around_api import actions, defs, geometry, inventory
from . import animating


class AnimationName:
    IDLE = "idle"
    WALK = "walk"
    PICK = "pick"
    DAMAGED = "damaged"
    SWING_LEFT = "swing_left"
    SWING_RIGHT = "swing_right"


class Animation(abc.ABC):
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
    def tick(self, interval, context: animating.AnimationContext) -> None:
        raise NotImplementedError("This animation is not implemented")


class ConfigurationAnimation(Animation):
    def __init__(self, action: actions.ConfigurationAction) -> None:
        super().__init__(None)
        self.hero_actor_id = action.hero_actor_id
        self.elevation = action.elevation

    def tick(self, interval, context: animating.AnimationContext) -> None:
        elevation = ear.ElevationFunction(self.elevation.radius)
        for terrain in self.elevation.terrain:
            origin = terrain.get_origin()
            elevation.add_terrain(terrain.get_name(), origin.theta, origin.phi)

        context.scene.configure(self.hero_actor_id, elevation)
        self.expire()


class CraftStartAnimation(Animation):
    def __init__(self, action: actions.CraftStartAction) -> None:
        super().__init__(None)
        self.crafter_id = action.crafter_id

    def tick(self, interval, context: animating.AnimationContext) -> None:
        self.expire()


class CraftEndAnimation(Animation):
    def __init__(self, action: actions.CraftEndAction) -> None:
        super().__init__(None)
        self.crafter_id = action.crafter_id

    def tick(self, interval, context: animating.AnimationContext) -> None:
        self.expire()


class CreateActorsAnimation(Animation):
    def __init__(self, action: actions.CreateActorsAction) -> None:
        super().__init__(None)
        self.actors = action.actors

    def tick(self, interval, context: animating.AnimationContext) -> None:
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
        self.expire()


class DeleteActorsAnimation(Animation):
    def __init__(self, action: actions.DeleteActorsAction) -> None:
        super().__init__(None)
        self.actor_ids = action.actor_ids

    def tick(self, interval, context: animating.AnimationContext) -> None:
        context.scene.delete_actors(self.actor_ids)
        context.world.delete_renderers(self.actor_ids)
        self.expire()


class MovementAnimation(Animation):
    def __init__(self, action: actions.MovementAction) -> None:
        super().__init__(action.duration)
        self.actor_id = action.actor_id
        self.speed = action.speed
        self.bearing = action.bearing
        self._tick_count = 0

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, interval, context: animating.AnimationContext) -> None:
        distance = self.speed * interval

        old_position = context.scene.get_actor_position(self.actor_id)
        old_point = geometry.Point(old_position.get_theta(), old_position.get_phi())
        new_point = old_point.moved_by(distance, self.bearing, context.scene.get_radius())
        new_position = ear.Point(new_point.theta, new_point.phi)
        context.scene.set_actor_position(self.actor_id, new_position)

        # TODO: Play animation
        # if self._tick_count == 0:
        #     context.world.play_animation(self.actor_id, AnimationName.WALK)

        self._tick_count += 1


class LocalizeAnimation(Animation):
    def __init__(self, action: actions.LocalizeAction) -> None:
        super().__init__(None)
        self.actor_id = action.actor_id
        self.position = action.position

    def get_actor_id(self) -> defs.ActorId:
        return self.actor_id

    def tick(self, interval, context: animating.AnimationContext) -> None:
        position = ear.Point(self.position.theta, self.position.phi)
        context.scene.set_actor_position(self.actor_id, position)
        # TODO: Play animation:
        # context.world.play_animation(self.actor_id, AnimationName.IDLE)
        self.expire()


class StatUpdateAnimation(Animation):
    def __init__(self, action: actions.StatUpdateAction) -> None:
        super().__init__(None)
        self.actor_id = action.actor_id
        self.stats = action.stats

    def tick(self, interval, context: animating.AnimationContext) -> None:
        context.gui.set_stats(self.stats)
        self.expire()


class PickStartAnimation(Animation):
    def __init__(self, action: actions.PickStartAction) -> None:
        super().__init__(None)
        self.actor_id = action.who
        self.item_id = action.what

    def tick(self, interval, context: animating.AnimationContext) -> None:
        # TODO: Play animation:
        # context.world.play_animation(self.actor_id, AnimationName.PICK)
        self.expire()


class PickEndAnimation(Animation):
    def __init__(self, action: actions.PickEndAction) -> None:
        super().__init__(None)
        self.actor_id = action.who

    def tick(self, interval, context: animating.AnimationContext) -> None:
        # TODO: Play animation:
        # context.world.play_animation(self.actor_id, AnimationName.IDLE)
        self.expire()


class UpdateInventoryAnimation(Animation):
    def __init__(self, action: actions.UpdateInventoryAction) -> None:
        super().__init__(None)
        self.owner_id = action.owner_id
        self.inventory = action.inventory

    def tick(self, interval, context: animating.AnimationContext) -> None:
        context.gui.set_inventory(self.inventory)

        context.scene.hide_actors(self.inventory.get_all_ids())

        left_item = self.inventory.get_hand(defs.Hand.LEFT)
        # TODO: attach skeleton:
        # context.world.attach_skeleton(self.owner_id, left_item, defs.Attachement.LEFT_ITEM)

        right_item = self.inventory.get_hand(defs.Hand.RIGHT)
        # TODO: attach skeleton:
        # context.world.attach_skeleton(self.owner_id, right_item, defs.Attachement.RIGHT_ITEM)

        self.expire()


class DamageAnimation(Animation):
    def __init__(self, action: actions.DamageAction) -> None:
        super().__init__(None)
        self.dealer_id = action.dealer_id
        self.receiver_id = action.receiver_id
        self.variant = action.variant
        self.hand = action.hand

    def tick(self, interval, context: animating.AnimationContext) -> None:
        # TODO: Play animations:
        # if self.hand == defs.Hand.LEFT:
        #    context.world.play_animation(self.dealer_id, AnimationName.SWING_LEFT)
        # else:
        #    context.world.play_animation(self.dealer_id, AnimationName.SWING_RIGHT)
        # context.world.play_animation(self.receiver_id, AnimationName.DAMAGED)

        # Play sounds
        context.sounds.play(self.variant.value)

        # Remove the animation
        self.expire()


_ANIMATION_CONSTRUCTORS: Dict[type, Any] = {
    actions.ConfigurationAction: ConfigurationAnimation,
    actions.CraftStartAction: CraftStartAnimation,
    actions.CraftEndAction: CraftEndAnimation,
    actions.CreateActorsAction: CreateActorsAnimation,
    actions.DeleteActorsAction: DeleteActorsAnimation,
    actions.MovementAction: MovementAnimation,
    actions.LocalizeAction: LocalizeAnimation,
    actions.StatUpdateAction: StatUpdateAnimation,
    actions.PickStartAction: PickStartAnimation,
    actions.PickEndAction: PickEndAnimation,
    actions.UpdateInventoryAction: UpdateInventoryAnimation,
    actions.DamageAction: DamageAnimation,
}


def animation_from_action(action: actions.Action) -> Optional[Animation]:
    """Converts an `Action` into an `Animation`."""

    return _ANIMATION_CONSTRUCTORS[type(action)](action)
