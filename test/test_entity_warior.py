import unittest

from src import actions, entities, events, jobs

class WariorTest(unittest.TestCase):
    def test_walking(self):
        id = 0
        bearing = 0.0
        duration = 1.0
        speed = 1.0

        warior = entities.Warior(id, position=(0.0, 0.0))

        result = warior.handle_event(events.ResumeEvent())
        self.assertIs(result.final_action, None)
        # Bearing is generated randomly. No need to check it.
        result.next_action.bearing = bearing
        result.next_job.bearing = bearing
        self.assertEqual(result.next_job, jobs.MovementJob(duration, events.FinishedEvent()))
        self.assertEqual(result.next_job.get_start_delay(), duration)
        self.assertEqual(result.next_action, actions.MovementAction(id, duration, bearing, speed))

        result = result.next_job.perform(warior)
        self.assertEqual(result.action, None)
        self.assertEqual(result.repeat, events.FinishedEvent())

        result = warior.handle_event(events.FinishedEvent())
        self.assertIs(result.final_action, None)
        result.next_action.bearing = bearing
        result.next_job.bearing = bearing
        self.assertEqual(result.next_job, jobs.MovementJob(duration, events.FinishedEvent()))
        self.assertEqual(result.next_job.get_start_delay(), duration)
        self.assertEqual(result.next_action, actions.MovementAction(id, duration, bearing, speed))

