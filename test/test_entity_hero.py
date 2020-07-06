import unittest

from src import actions, defs, entities, essentials, events, generator, geometry, jobs

class HeroTest(unittest.TestCase):
    def test_resume(self):
        hero = entities.Hero(0, position=geometry.Point(0.0, 0.0))
        world = generator.WorldGenerator().generate_basic(100.0)
        world.entities = {0: hero}

        old = hero.get_task()
        hero.handle_event(events.ResumeEvent())
        new = hero.get_task()
        self.assertTrue(isinstance(old, essentials.IdleTask))
        self.assertTrue(isinstance(new, essentials.IdleTask))
        self.assertEqual(old.finish(world), list())
        self.assertEqual(new.get_job(), None)
        self.assertEqual(new.start(world), list())

    def test_movement(self):
        id = 0
        bearing = 0.0
        interval = 0.1
        max_duration = 20.0
        speed = 1.0

        hero = entities.Hero(0, position=geometry.Point(0.0, 0.0))
        world = generator.WorldGenerator().generate_basic(100.0)
        world.entities = {0: hero}

        old = hero.get_task()
        hero.handle_event(events.StartMovingEvent(bearing))
        new = hero.get_task()
        self.assertIsNot(old, new)
        final_actions, job, start_actions = old.finish(world), new.get_job(), new.start(world)
        self.assertEqual(final_actions, list())
        self.assertEqual(job, jobs.MovementJob(speed, bearing, max_duration, None))
        self.assertEqual(job.get_start_delay(), interval)
        self.assertEqual(start_actions, [actions.MovementAction(id, speed, bearing, max_duration)])

        old = hero.get_task()
        hero.handle_event(events.StopMovingEvent())
        new = hero.get_task()
        self.assertIsNot(old, new)
        final_actions, job, start_actions = old.finish(world), new.get_job(), new.start(world)
        self.assertTrue(isinstance(final_actions[0], actions.LocalizeAction))
        self.assertEqual(job, None)
        self.assertEqual(start_actions, list())

    def test_picking(self):
        hero_id, far_id, close_id = 0, 1, 2
        hero = entities.Hero(hero_id, position=geometry.Point(0.0, 0.0))
        far_object = entities.Rocks(far_id, position=geometry.Point(10.0, 10.0))
        close_object = entities.Rocks(close_id, position=geometry.Point(10.0, 10.0))

        world = generator.WorldGenerator().generate_basic(100.0)
        world.entities = {hero_id: hero, far_id: far_object, close_id: close_object}

        # Try to pick an item that is out of range
        old = hero.get_task()
        hero.handle_event(events.HandActivationEvent(defs.Hand.RIGHT, close_id))
        new = hero.get_task()
        self.assertIsNot(old, new)
        final_actions, job, start_actions = old.finish(world), new.get_job(), new.start(world)
        self.assertEqual(final_actions, list())
        self.assertEqual(job, jobs.WaitJob(hero.PICK_TIMEOUT, None))
        self.assertEqual(job.get_start_delay(), hero.PICK_TIMEOUT)
        self.assertEqual(start_actions, [actions.PickStartAction(who=hero_id, what=close_id)])

        # Try to pick an item that is withing range
        old = hero.get_task()
        hero.handle_event(events.HandActivationEvent(defs.Hand.RIGHT, close_id))
        new = hero.get_task()
        self.assertIsNot(old, new)
        final_actions, job, start_actions = old.finish(world), new.get_job(), new.start(world)
        self.assertEqual(final_actions, list())
        self.assertEqual(job, jobs.WaitJob(hero.PICK_TIMEOUT, None))
        self.assertEqual(job.get_start_delay(), hero.PICK_TIMEOUT)
        self.assertEqual(start_actions, [actions.PickStartAction(who=hero_id, what=close_id)])

