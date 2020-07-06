import time

from typing import Dict, Optional, Union

from . import actions, essentials, events, executor, jobs, scene, state

HERO_ENTITY_ID = 0


class ClientInfo:
    def __init__(self, hero_entity_id):
        self.hero_entity_id = hero_entity_id


class Engine(executor.Processor):
    def __init__(self, proxy, state: state.State) -> None:
        self.state = state
        self.proxy = proxy
        self.clients: Dict[int, ClientInfo] = dict()

    def start(self, scheduler) -> None:
        self.scheduler = scheduler
        for entity in self.state.get_entities():
            entity_id = entity.get_id()
            if entity.features.performer is not None:
                self.run(None, entity_id=entity_id, trigger=events.ResumeEvent())
            if entity.features.eater is not None:
                self.run(None, entity_id=entity_id, trigger=jobs.HungerDrainJob())

    def run(self, handle: Optional[int], **kwargs) -> None:
        entity_id: essentials.EntityId = kwargs['entity_id']
        trigger: Union[events.Event, essentials.Job] = kwargs['trigger']

        entity = self.state.get_entity(entity_id)

        if entity is not None:
            if isinstance(trigger, essentials.Job):
                self._handle_job(handle, entity, trigger)

            elif isinstance(trigger, events.Event):
                self._handle_event(entity, trigger)

    def handle_event(self, client_id: int, event: events.Event) -> None:
        client = self.clients[client_id]
        self.run(None, entity_id=client.hero_entity_id, trigger=event)

    def handle_connection(self, client_id: int) -> None:
        actors = [scene.Actor(
                entity.id, entity.position, entity.get_name(),
            ) for entity in self.state.get_entities()]

        self.clients[client_id] = ClientInfo(HERO_ENTITY_ID)

        self.proxy.send_action(actions.ConfigurationAction(
            HERO_ENTITY_ID,
            self.state.elevation_function,
        ))
        self.proxy.send_action(actions.CreateActorsAction(actors))

    def _handle_job(self,
            handle: executor.JobHandle,
            entity: essentials.Entity,
            job: essentials.Job,
        ) -> None:
        result = job.perform(entity, self.state)

        for action in result.actions:
            self.proxy.send_action(action)

        if isinstance(result.repeat, float):
            self.scheduler.enter(handle, result.repeat, entity_id=entity.get_id(), trigger=job)
        elif isinstance(result.repeat, events.Event):
            self.scheduler.enter(None, 0.0, entity_id=entity.get_id(), trigger=result.repeat)

    def _handle_event(self, entity: essentials.Entity, event: events.Event) -> None:
        old_task = entity.get_task()
        entity.handle_event(event)
        new_task = entity.get_task()

        if old_task is not new_task:
            for action in old_task.finish(self.state):
                self.proxy.send_action(action)

            next_job = new_task.get_job()
            self.scheduler.cancel(handle=entity.get_id())
            if next_job is not None:
                self.scheduler.enter(
                        handle=entity.get_id(),
                        delay=next_job.get_start_delay(),
                        entity_id=entity.get_id(),
                        trigger=next_job,
                    )

            for action in new_task.start(self.state):
                self.proxy.send_action(action)

