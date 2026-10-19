import unittest
from unittest.mock import Mock, patch

from src.config import INITIAL_STATS
from src.event_system import EventSystem
from src.session import GameSession


class EventSystemTests(unittest.TestCase):
    def setUp(self):
        self.stats = dict(INITIAL_STATS, world_state='no_rain')
        self.events = EventSystem('data/events.json', 'data/ambient.json', self.stats)

    def event(self, event_id):
        return next(e for e in self.events.events_all if e['id'] == event_id)

    def test_first_event_waits_and_uses_simulation_time(self):
        self.events._major_remaining = 12
        with patch('time.time', return_value=9999999999):
            self.events.update(0)
            self.assertIsNone(self.events.current_event)
            self.events.update(12)
            self.assertIsNotNone(self.events.current_event)

    def test_choice_is_applied_once_and_closes_atomically(self):
        self.events._begin_event(self.event('phone_doomscroll'))
        self.assertTrue(self.events.choose_option(0))
        self.assertEqual(self.stats['reality'], 66)
        self.assertIsNone(self.events.current_event)
        self.assertFalse(self.events.choose_option(0))
        self.assertEqual(self.stats['reality'], 66)

    def test_choice_timeout_is_neutral_and_invalid_index_is_safe(self):
        self.events._begin_event(self.event('drowsy'))
        self.assertFalse(self.events.choose_option(99))
        before = self.stats.copy()
        self.events.update(8)
        self.assertEqual(self.stats, before)
        self.assertIsNone(self.events.current_event)

    def test_weather_switches_immediately_and_stop_uses_play_time(self):
        self.events._begin_event(self.event('rain_starts'))
        self.assertEqual(self.stats['world_state'], 'rain')
        self.events.dismiss_event()
        self.assertFalse(self.events._allowed(self.event('rain_stops')))
        self.events._elapsed = 30
        self.assertTrue(self.events._allowed(self.event('rain_stops')))
        self.events._major_remaining = self.events._ambient_remaining = 1000
        self.events.update(30)
        self.assertEqual(self.events.current_event['id'], 'rain_stops')
        self.assertEqual(self.stats['world_state'], 'no_rain')

    def test_reset_removes_weather_and_event_runtime_fields(self):
        self.events._begin_event(self.event('rain_starts'))
        self.events.current_event['_wait_animation'] = True
        self.events.reset()
        self.assertIsNone(self.events._rain_start_time)
        self.assertIsNone(self.events.current_event)
        self.assertNotIn('_wait_animation', self.event('rain_starts'))

    def test_ambient_legacy_and_mixed_content_is_available(self):
        candidates = self.events._get_available_ambient()
        self.assertIn('ai_actually_worked', [e['id'] for e in candidates])
        stack = next(e for e in candidates if e['id'] == 'ambient_stack')
        self.events._apply(stack['effects'])
        self.assertEqual(self.stats['reality'], 62)

    def test_ambient_log_is_bounded_and_done_has_no_ambient(self):
        self.events._major_remaining = 10000
        for _ in range(20):
            self.events._ambient_remaining = 0
            self.events.update(0)
        self.assertEqual(len(self.events.ambient_log), 6)
        self.stats['world_state'] = 'done'
        self.assertEqual(self.events._get_available_ambient(), [])
        self.assertTrue(all(e['domain'] == 'done' for e in self.events._get_available_events()))

    def test_unsupported_sunrise_cannot_break_animation_domain(self):
        self.events._apply({'world_state': 'sunrise', 'vibe': 20})
        self.assertEqual(self.stats['world_state'], 'no_rain')
        self.assertEqual(self.stats['vibe'], 50)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.sprite = Mock()
        self.sprite.is_finished.return_value = False
        self.session = GameSession(self.sprite)
        self.session.start(1)

    def test_second_session_shares_stats_and_clears_runtime_state(self):
        stats = self.session.stats
        self.session.events._begin_event(next(e for e in self.session.events.events_all if e['id'] == 'rain_starts'))
        self.session.state.set_animation_chain([('cat_down', None)])
        self.session.start(0)
        self.assertIs(self.session.stats, stats)
        self.assertIs(self.session.events.stats, stats)
        self.assertEqual(stats['world_state'], 'no_rain')
        self.assertFalse(self.session.state.is_chain_active)
        self.session.events._apply({'reality': -5})
        self.assertEqual(stats['reality'], 55)

    def test_done_interrupts_chain_discards_old_event_without_effects(self):
        self.session.events._begin_event(next(e for e in self.session.events.events_all if e['id'] == 'cat_on_keyboard'))
        self.session.stats['reality'] = 0
        self.session.update(0)
        self.assertEqual(self.session.state.domain, 'done')
        self.assertEqual(self.session.stats['_done_reason'], 'sanity')
        self.assertEqual(self.session.stats['vibe'], INITIAL_STATS['vibe'])
        self.assertIsNone(self.session.events.current_event)
        self.assertFalse(self.session.state.is_chain_active)

    def test_progress_done_only_triggers_done_events_and_freezes_stats(self):
        self.session.stats['progress'] = 100
        self.session.update(0)
        self.assertEqual(self.session.stats['_done_reason'], 'progress')
        self.assertEqual(self.session.events.current_event['domain'], 'done')
        before = self.session.stats.copy()
        self.session.update(1)
        self.assertEqual(self.session.stats, before)

    def test_animation_completion_does_not_erase_choices(self):
        self.session.events._begin_event(next(e for e in self.session.events.events_all if e['id'] == 'phone_doomscroll'))
        self.sprite.is_finished.return_value = True
        self.session.update(0)
        self.assertEqual(self.session.events.current_event['id'], 'phone_doomscroll')


if __name__ == '__main__':
    unittest.main()
