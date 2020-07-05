import unittest

from src import actions, defs, entities, essentials, events, jobs, state

class HeroTest(unittest.TestCase):
    def test_resume(self):
        hero = entities.Hero(0, position=(0.0, 0.0))
        result = hero.handle_event(events.ResumeEvent())
        self.assertEqual(result, essentials.EventResult(None, None, None))

    def test_movement(self):
        id = 0
        bearing = 0.0
        max_duration = 20.0
        speed = 1.0

        hero = entities.Hero(id, position=(0.0, 0.0))

        result = hero.handle_event(events.StartMovingEvent(bearing))
        self.assertIs(result.final_action, None)
        self.assertEqual(result.next_job, jobs.MovementJob(max_duration, None))
        self.assertEqual(result.next_job.get_start_delay(), max_duration)
        self.assertEqual(result.next_action, actions.MovementAction(id, max_duration, bearing, speed))

        result = result.next_job.perform(hero)
        self.assertIs(result.action, None)
        self.assertEqual(result.repeat, None)

        result = hero.handle_event(events.StopMovingEvent())
        self.assertEqual(result.final_action, actions.LocalizeAction(id))
        self.assertIs(result.next_job, None)
        self.assertIs(result.next_action, None)

    def test_picking(self):
        hero_id, far_id, close_id = 0, 1, 2
        hero = entities.Hero(hero_id, position=(0.0, 0.0))
        far_object = entities.Rocks(far_id, position=(10.0, 10.0))
        close_object = entities.Rocks(close_id, position=(10.0, 10.0))

        world = state.WorldGenerator().generate_basic(100.0)
        world.entities = [hero, far_object, close_object]

        # Try to pick an item that is out of range
        result = hero.handle_event(events.HandActivationEvent(defs.Hand.RIGHT, close_id))
        self.assertIs(result.final_action, None)
        self.assertIs(result.next_job, None)
        self.assertIs(result.next_action, None)

        # Try to pick an item that is withing range
        result = hero.handle_event(events.HandActivationEvent(defs.Hand.RIGHT, close_id))
        self.assertIs(result.final_action, None)
        self.assertEqual(result.next_job, jobs.PickItemJob(hero_id, close_id, hero.PICK_TIMEOUT))
        self.assertEqual(result.next_job.get_start_delay(), hero.PICK_TIMEOUT)
        self.assertEqual(result.next_action, actions.PickStartAction(who=hero_id, what=close_id))

        result = result.next_job.perform(hero)
        self.assertEqual(result.action, actions.PickEndAction(who=hero_id, what=close_id))
        self.assertEqual(result.repeat, None)

