import time

from typing import Dict, Optional, Union

from . import actions, defs, essentials, events, executor, jobs, scene, state

HERO_ENTITY_ID = 0


class ClientInfo:
    def __init__(self, hero_entity_id):
        self.hero_entity_id = hero_entity_id


class Engine(executor.Processor):
    def __init__(self, proxy, state: state.State) -> None:
        self.state = state
        self.proxy = proxy
        self.clients: Dict[int, ClientInfo] = dict()

    def get_hero_id_for_client(self, client_id: int) -> Optional[defs.ActorId]:
        client = self.clients[client_id]
        return client.hero_entity_id if client is not None else None

    def start(self, scheduler) -> None:
        self.scheduler = scheduler
        for entity in self.state.get_entities():
            entity_id = entity.get_id()
            if entity.features.performer is not None:
                self.run(None, trigger=events.ResumeEvent(entity_id))
            if entity.features.eater is not None:
                self.run(None, trigger=jobs.HungerDrainJob(entity_id))

    def run(self, handle: Optional[int], **kwargs) -> None:
        trigger: Union[events.Event, essentials.Job] = kwargs['trigger']

        if isinstance(trigger, essentials.Job):
            self._handle_job(handle, trigger)

        elif isinstance(trigger, events.Event):
            self._handle_event(trigger)

    def handle_event(self, event: events.Event) -> None:
        self.run(None, trigger=event)

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

    def _handle_job(self, handle: executor.JobHandle, job: essentials.Job) -> None:
        result = job.perform(self.state)

        for action in result.actions:
            self.proxy.send_action(action)

        for event in result.events:
            self.scheduler.enter(None, 0.0, entity_id=event.get_receiver_id(), trigger=event)

        if result.repeat is not None:
            self.scheduler.enter(handle, result.repeat, trigger=job)

    def _handle_event(self, event: events.Event) -> None:
        entity = self.state.get_entity(event.get_receiver_id())
        if entity is None:
            return

        old_task = entity.get_task()
        entity.handle_event(event)
        new_task = entity.get_task()

        if old_task is not new_task:
            for action in old_task.finish(self.state):
                self.proxy.send_action(action)

            for action in new_task.start(self.state):
                self.proxy.send_action(action)

            next_job = new_task.get_job()
            self.scheduler.cancel(handle=entity.get_id())
            if next_job is not None:
                self.scheduler.enter(
                        handle=entity.get_id(),
                        delay=next_job.get_start_delay(),
                        trigger=next_job,
                    )

