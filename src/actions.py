from typing import List

from . import animations, geometry, scene

class Action:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return 'Action'

    def into_animation(self) -> animations.Animation:
        raise NotImplementedError('This action cannot be casted to an animation')


class ConfigurationAction(Action):
    def __init__(self, elevation_function: geometry.ElevationFunction) -> None:
        super().__init__()
        self.elevation_function = elevation_function

    def __str__(self) -> str:
        return 'ConfigurationAction'

    def into_animation(self) -> animations.ConfigurationAnimation:
        return animations.ConfigurationAnimation(self.elevation_function)


class CreateActorsAction(Action):
    def __init__(self, actors: List[scene.Actor]) -> None:
        super().__init__()
        self.actors = actors

    def __str__(self) -> str:
        ids = [actor.id for actor in self.actors]
        return f'CreateActorsAction({ids=})'

    def into_animation(self) -> animations.CreateActorsAnimation:
        return animations.CreateActorsAnimation(self.actors)


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

