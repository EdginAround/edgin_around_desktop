import time

from typing import Dict

from . import actions, entity, events, scene, state, tasks

HERO_ENTITY_ID = 0

class ClientInfo:
    def __init__(self, hero_entity_id):
        self.hero_entity_id = hero_entity_id

class Engine:
    def __init__(self, proxy, state: state.State) -> None:
        self.state = state
        self.proxy = proxy
        self.clients: Dict[int, ClientInfo] = dict()

    def start(self, scheduler) -> None:
        for performer in self.state.get_performers():
            self.run(scheduler, entity=performer, event=events.ResumeEvent())

    def run(self, scheduler, entity: entity.Entity, event: events.Event) -> None:
        task = self._handle_entity_event(entity, event)
        if task is not None:
            scheduler.enter(task.get_timeout(), entity=entity, event=events.FinishedEvent())

    def handle_event(self, client_id: int, event: events.Event) -> None:
        if isinstance(event, events.ConnectionEvent):
            self._handle_connection_event(client_id, event)

        else:
            client = self.clients[client_id]
            entity = self.state.get_entity(client.hero_entity_id)
            if entity is not None:
                self._handle_entity_event(entity, event)

    def _handle_connection_event(self, client_id: int, event: events.ConnectionEvent) -> None:
        actors = [scene.Actor(
                entity.id, entity.position[0], entity.position[1], entity.get_name(),
            ) for entity in self.state.get_entities()]

        self.clients[client_id] = ClientInfo(HERO_ENTITY_ID)

        self.proxy.send_action(actions.ConfigurationAction(
            HERO_ENTITY_ID,
            self.state.elevation_function,
        ))
        self.proxy.send_action(actions.CreateActorsAction(actors))

    def _handle_entity_event(
            self,
            entity: entity.Entity,
            event: events.Event,
        ) -> tasks.Task:
        final_action, new_task = entity.handle_event(event)
        if final_action is not None:
            self.proxy.send_action(final_action)

        new_action = new_task.get_action()
        if new_action is not None:
            self.proxy.send_action(new_action)

        return new_task

