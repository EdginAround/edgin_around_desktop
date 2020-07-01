import time

from typing import Dict, Union

from . import actions, entity, events, jobs, scene, state, tasks

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
        self.scheduler = scheduler
        for entity in self.state.get_entities():
            entity_id = entity.get_id()
            if entity.features.performer is not None:
                self.run(entity_id=entity_id, trigger=events.ResumeEvent())
            if entity.features.eater is not None:
                self.run(entity_id=entity_id, trigger=jobs.HungerDrainJob())

    def run(self, entity_id: entity.EntityId, trigger: Union[events.Event, jobs.Job]) -> None:
        entity = self.state.get_entity(entity_id)

        if entity is not None:
            if isinstance(trigger, jobs.Job):
                self._handle_job(entity, trigger)

            elif isinstance(trigger, events.Event):
                self._handle_event(entity, trigger)

    def handle_event(self, client_id: int, event: events.Event) -> None:
        client = self.clients[client_id]
        self.run(client.hero_entity_id, event)

    def handle_connection(self, client_id: int) -> None:
        actors = [scene.Actor(
                entity.id, entity.position[0], entity.position[1], entity.get_name(),
            ) for entity in self.state.get_entities()]

        self.clients[client_id] = ClientInfo(HERO_ENTITY_ID)

        self.proxy.send_action(actions.ConfigurationAction(
            HERO_ENTITY_ID,
            self.state.elevation_function,
        ))
        self.proxy.send_action(actions.CreateActorsAction(actors))

    def _handle_job(self, entity: entity.Entity, job: jobs.Job) -> None:
        action = entity.handle_job(job)
        if action is not None:
            self.proxy.send_action(action)

        if job.get_repeat_delay() is not None:
            self.scheduler.enter(job.get_repeat_delay(), entity_id=entity.get_id(), trigger=job)

    def _handle_event(self, entity: entity.Entity, event: events.Event) -> None:
        final_action, new_task = entity.handle_event(event)
        if final_action is not None:
            self.proxy.send_action(final_action)

        new_action = new_task.get_action()
        if new_action is not None:
            self.proxy.send_action(new_action)

        self.scheduler.enter(
                new_task.get_timeout(),
                entity_id=entity.get_id(),
                trigger=events.FinishedEvent(),
            )

