from typing import List

from . import animations, defs, geometry, inventory, scene

class Action:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return 'Action'

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def into_animation(self) -> animations.Animation:
        raise NotImplementedError('This action cannot be casted to an animation')


class ConfigurationAction(Action):
    def __init__(self, hero_actor_id: int, elevation_function: geometry.ElevationFunction) -> None:
        super().__init__()
        self.hero_actor_id = hero_actor_id
        self.elevation_function = elevation_function

    def __str__(self) -> str:
        return 'ConfigurationAction'

    def into_animation(self) -> animations.ConfigurationAnimation:
        return animations.ConfigurationAnimation(self.hero_actor_id, self.elevation_function)


class CreateActorsAction(Action):
    def __init__(self, actors: List[scene.Actor]) -> None:
        super().__init__()
        self.actors = actors

    def __str__(self) -> str:
        ids = [actor.id for actor in self.actors]
        return f'CreateActorsAction({ids=})'

    def into_animation(self) -> animations.CreateActorsAnimation:
        return animations.CreateActorsAnimation(self.actors)


class DeleteActorsAction(Action):
    def __init__(self, actor_ids: List[defs.ActorId]) -> None:
        super().__init__()
        self.actor_ids = actor_ids

    def __str__(self) -> str:
        return f'DeleteActorsAction(ids={self.actor_ids})'

    def into_animation(self) -> animations.DeleteActorsAnimation:
        return animations.DeleteActorsAnimation(self.actor_ids)


class MovementAction(Action):
    def __init__(self, actor_id, duration, bearing, speed) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.duration = duration
        self.bearing = bearing
        self.speed = speed

    def __str__(self) -> str:
        return f'MovementAction(actor_id={self.actor_id}, duration={self.duration},' \
            ' bearing={self.bearing}, speed={self.speed})'

    def into_animation(self) -> animations.MovementAnimation:
        return animations.MovementAnimation(
                self.duration,
                self.actor_id,
                self.bearing,
                self.speed,
            )

class LocalizeAction(Action):
    def __init__(self, actor_id: defs.ActorId) -> None:
        super().__init__()
        self.actor_id = actor_id

    def __str__(self) -> str:
        return f'LocalizeAction(actor_id={self.actor_id})'

    def into_animation(self) -> animations.LocalizeAnimation:
        return animations.LocalizeAnimation(self.actor_id)


class StatUpdateAction(Action):
    def __init__(self, actor_id: defs.ActorId, stats: defs.Stats) -> None:
        super().__init__()
        self.actor_id = actor_id
        self.stats = stats

    def __str__(self) -> str:
        return f'StatUpdateAction(hunger={self.stats.hunger}/{self.stats.max_hunger})'

    def into_animation(self) -> animations.StatUpdateAnimation:
        return animations.StatUpdateAnimation(self.actor_id, self.stats)


class PickStartAction(Action):
    def __init__(self, who: defs.ActorId, what: defs.ActorId) -> None:
        super().__init__()
        self.who = who
        self.what = what

    def __str__(self) -> str:
        return f'PickStartAction(who={self.who}, what={self.what})'

    def into_animation(self) -> animations.PickStartAnimation:
        return animations.PickStartAnimation(self.who, self.what)


class PickEndAction(Action):
    def __init__(self, who: defs.ActorId, what: defs.ActorId) -> None:
        super().__init__()
        self.who = who
        self.what = what

    def __str__(self) -> str:
        return f'PickEndAction(who={self.who}, what={self.what})'

    def into_animation(self) -> animations.PickEndAnimation:
        return animations.PickEndAnimation(self.who, self.what)


class UpdateInventoryAction(Action):
    def __init__(self, inventory: inventory.Inventory) -> None:
        super().__init__()
        self.inventory = inventory

    def __str__(self) -> str:
        return f'UpdateInventoryAction'

    def into_animation(self) -> animations.UpdateInventoryAnimation:
        return animations.UpdateInventoryAnimation(self.inventory)

