import unittest
from unittest.mock import MagicMock, patch

import pygame

from src.audio_manager import AudioManager, FADE_DURATION
from src.sprite_engine import SpritePlayer
from src.state_manager import StateManager


class StateManagerTests(unittest.TestCase):
    def setUp(self):
        self.transitions = []
        self.state = StateManager(lambda *args: self.transitions.append(args))

    def test_done_interrupts_chain_and_rain_idle(self):
        for source in ("cat_wake", "rain_idle"):
            with self.subTest(source=source):
                self.state.reset()
                self.state.current_animation = source
                self.state.set_animation_chain([("cat_down", None)])
                self.state.request_animation("done")
                self.assertEqual(self.transitions[-1], ("done", "fade", False))
                self.assertFalse(self.state.is_chain_active)
                self.state.on_animation_finished()
                self.assertEqual(self.state.current_animation, "done")

    def test_chain_keeps_lock_until_final_animation_finishes(self):
        self.state.request_animation("cat_wake")
        self.state.set_animation_chain([("cat_type_remove", "direct"), ("cat_down", "direct")])
        for expected in ("cat_type_remove", "cat_down"):
            self.state.on_animation_finished()
            self.assertEqual(self.state.current_animation, expected)
            self.state.request_animation("phone")
            self.assertEqual(self.state.current_animation, expected)
            self.assertTrue(self.state.is_chain_active)
        self.state.on_animation_finished()
        self.assertFalse(self.state.is_chain_active)
        self.assertIn(self.state.current_animation, self.state.idle_pool)

    def test_reset_clears_domain_chain_and_timers(self):
        self.state.domain = "done"
        self.state.set_animation_chain([("cat_down", None)])
        self.state._idle_timer = 20
        self.state._cat_watch_timer = 10
        self.state.reset()
        self.assertEqual(self.state.domain, "no_rain")
        self.assertFalse(self.state.is_chain_active)
        self.assertEqual(self.state._idle_timer, 0)
        self.assertEqual(self.state._cat_watch_timer, 0)
        self.assertEqual(self.transitions[-1], ("idle1", None, True))

    def test_rain_idle_wake_fades_but_rain_wake_is_direct(self):
        self.state.domain = "rain"
        self.state.current_animation = "rain_idle"
        self.state.request_animation("rain_cat_wake")
        self.assertEqual(self.transitions[-1], ("rain_cat_wake", "fade", False))
        self.state.current_animation = "rain"
        self.state.request_animation("rain_cat_wake")
        self.assertEqual(self.transitions[-1], ("rain_cat_wake", None, False))


class SpritePlayerTests(unittest.TestCase):
    def setUp(self):
        self.player = SpritePlayer()
        self.frames = [pygame.Surface((2, 2), pygame.SRCALPHA) for _ in range(3)]
        for index, frame in enumerate(self.frames):
            frame.fill((index * 80, 0, 0))
        self.player.sequences["test"] = self.frames

    def test_last_frame_has_full_duration(self):
        self.player.play("test")
        self.player.update(2 / self.player.fps)
        self.assertEqual(self.player.frame_index, 2)
        self.assertFalse(self.player.is_finished())
        self.player.update(1 / self.player.fps)
        self.assertTrue(self.player.is_finished())
        self.assertIs(self.player.get_frame(), self.frames[-1])

    def test_switch_resets_timer_and_uses_visible_frame(self):
        self.player.play("test")
        self.player.update(0.14)
        self.assertEqual(self.player.frame_index, 1)
        self.player.sequences["next"] = [pygame.Surface((2, 2))]
        self.player.play("next", "fade")
        self.assertEqual(self.player.old_frame.get_at((0, 0)), self.frames[1].get_at((0, 0)))
        self.assertEqual(self.player._timer, 0)
        self.assertFalse(self.player.is_finished())
        self.player.update(self.player.transition_duration)
        self.assertFalse(self.player.is_finished())
        self.player.update(1 / self.player.fps)
        self.assertTrue(self.player.is_finished())

    def test_missing_or_empty_sequence_is_explicit_and_keeps_current(self):
        self.player.play("test")
        for name in ("missing", "empty"):
            self.player.sequences["empty"] = []
            with self.assertRaises(ValueError):
                self.player.play(name)
            self.assertEqual(self.player.current_seq, "test")

    def test_lazy_registration_and_lru_eviction(self):
        self.player.max_cached_frames = 3
        image = MagicMock()
        image.convert_alpha.return_value = self.frames[0]
        with patch("src.sprite_engine.glob.glob", return_value=["frame.png"]), patch(
            "src.sprite_engine.pygame.image.load", return_value=image
        ) as load:
            for name in ("a", "b", "c", "d"):
                self.player.load_sequence(name, name, loop=True)
            load.assert_not_called()
            for name in ("a", "b", "c", "a", "d"):
                self.player.play(name)
                self.player.get_frame()
            self.assertEqual(load.call_count, 4)
            self.assertNotIn(("b", 0), self.player._frame_cache)
            self.assertEqual(len(self.player._frame_cache), 3)
            self.assertTrue(self.player.loop)

    def test_long_sequence_switch_decodes_only_rendered_frames(self):
        image = MagicMock()
        image.convert_alpha.return_value = self.frames[0]
        paths = [f"frame_{index:03d}.png" for index in range(120)]
        with patch("src.sprite_engine.glob.glob", return_value=paths), patch(
            "src.sprite_engine.pygame.image.load", return_value=image
        ) as load:
            self.player.load_sequence("long", "long")
            self.player.play("long")
            load.assert_not_called()
            self.player.get_frame()
            self.assertEqual(load.call_count, 1)
            self.player.get_frame()
            self.assertEqual(load.call_count, 1)
            for _ in range(119):
                self.player.update(1 / self.player.fps)
                self.player.get_frame()
                self.assertLessEqual(len(self.player._frame_cache), 96)
            self.assertFalse(self.player.is_finished())
            self.player.update(1 / self.player.fps)
            self.assertTrue(self.player.is_finished())
            self.assertEqual(load.call_count, 120)


class AudioManagerTests(unittest.TestCase):
    def make_audio(self):
        channels = [MagicMock(), MagicMock()]
        with patch("src.audio_manager.pygame.mixer.get_init", return_value=(44100, -16, 2)), patch(
            "src.audio_manager.pygame.mixer.Channel", side_effect=channels
        ), patch.object(AudioManager, "_load_all"):
            manager = AudioManager()
        manager._playlists = {name: [name + ".mp3"] for name in ("no_rain", "done", "low_reality")}
        return manager, channels

    def test_missing_audio_device_or_directory_is_safe(self):
        with patch("src.audio_manager.pygame.mixer.get_init", return_value=None), patch(
            "src.audio_manager.pygame.mixer.init", side_effect=pygame.error("no device")
        ):
            manager = AudioManager()
            manager.set_volume(0.8)
            manager.toggle_mute()
            manager.update("done", 0, 1)
            manager.stop()
        with patch("src.audio_manager.os.path.isdir", return_value=False):
            manager._load_all()

    def test_done_takes_priority_even_during_fade(self):
        manager, _ = self.make_audio()
        with patch("src.audio_manager.pygame.mixer.Sound") as sound:
            manager.update("no_rain", 60, 0.5)
            manager.update("done", 0, FADE_DURATION)
        self.assertEqual(sound.call_args.args, ("done.mp3",))
        self.assertEqual(manager._current_domain, "done")

    def test_volume_and_mute_preserve_crossfade_and_time(self):
        manager, channels = self.make_audio()
        with patch("src.audio_manager.pygame.mixer.Sound"):
            manager.update("no_rain", 60, FADE_DURATION / 2)
            manager.set_volume(0.8)
            channels[0].set_volume.assert_called_with(0.4)
            channels[1].set_volume.assert_called_with(0.4)
            manager.toggle_mute()
            for channel in channels:
                channel.set_volume.assert_called_with(0)
            manager.update("done", 0, FADE_DURATION)
            self.assertEqual(manager._current_domain, "done")
            for channel in channels:
                channel.set_volume.assert_called_with(0)
            manager.toggle_mute()
            manager._active_ch.set_volume.assert_called_with(0.8)
            manager.stop()
            self.assertFalse(manager._fading)
            self.assertIsNone(manager._next_domain)


if __name__ == "__main__":
    unittest.main()
