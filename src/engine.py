import time

from . import entity, events, actions, world_state, tasks, scene

class Engine:
    def __init__(self, proxy, state: world_state.WorldState) -> None:
        self.state = state
        self.proxy = proxy

    def start(self, scheduler) -> None:
        for performer in self.state.get_performers():
            self.run(scheduler, performer=performer, event=events.ResumeEvent())

    def run(self, scheduler, performer: entity.Entity, event: events.Event) -> None:
        task = performer.handle_event(event)
        action = task.get_action()
        if action is not None:
            self.proxy.send_action(action)

        scheduler.enter(task.get_timeout(), performer=performer, event=events.FinishedEvent())

    def handle_event(self, event) -> None:
        if isinstance(event, events.ConnectionEvent):
            self._handle_connection_event(event)

    def _handle_connection_event(self, event: events.ConnectionEvent) -> None:
        actors = [scene.Actor(
                entity.id, entity.position[0], entity.position[1], entity.get_name(),
            ) for entity in self.state.entities]

        self.proxy.send_action(actions.ConfigurationAction(self.state.elevation_function))
        self.proxy.send_action(actions.CreateActorsAction(actors))

