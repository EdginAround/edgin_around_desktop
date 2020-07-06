import unittest

from src import actions, entities, events, generator, geometry, jobs

class WariorTest(unittest.TestCase):
    def test_walking(self):
        id = 0
        bearing = 0.0
        interval = 0.1
        duration = 1.0
        speed = 1.0

        warior = entities.Warior(id, position=geometry.Point(0.0, 0.0))

        world = generator.WorldGenerator().generate_basic(100.0)
        world.entities = {id: warior}

        for i, event in enumerate([events.ResumeEvent(), events.FinishedEvent()]):
            old_task = warior.get_task()
            warior.handle_event(event)
            new_task = warior.get_task()
            self.assertIsNot(old_task, new_task)

            final_actions = old_task.finish(world)
            if i == 0:
                self.assertEqual(len(final_actions), 0)
            else:
                self.assertEqual(len(final_actions), 1)
                self.assertTrue(isinstance(final_actions[0], actions.LocalizeAction))

            start_actions = new_task.start(world)
            job = new_task.get_job()
            self.assertEqual(len(start_actions), 1)
            # Bearing is generated randomly. No need to check it.
            start_actions[0].bearing = bearing
            job.bearing = bearing
            expected_job = jobs.MovementJob(speed, bearing, duration, events.FinishedEvent())
            self.assertEqual(job, expected_job)
            self.assertEqual(job.get_start_delay(), interval)
            self.assertEqual(start_actions, [actions.MovementAction(id, duration, bearing, speed)])

