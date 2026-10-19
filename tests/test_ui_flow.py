"""真实素材 + SDL 离屏渲染：输入路由、布局和完整重开流程。"""
import os
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame

from main import Game
from src import ui
from src.font_manager import set_lang
from src.config import SPRITE_DIR, resource_path


@unittest.skipUnless(
    Path(SPRITE_DIR).is_dir()
    and Path(resource_path('assets/fonts/FusionPixel10.ttf')).is_file()
    and Path(resource_path('assets/fonts/PressStart2P-Regular.ttf')).is_file(),
    'Runtime assets are excluded from the source showcase; see docs/ASSET_SETUP.md',
)
class UiFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()

    @classmethod
    def tearDownClass(cls):
        cls.game.close()

    def setUp(self):
        self.game._return_to_menu()
        self.game.running = True
        self.game.screen = pygame.display.set_mode((960, 540), pygame.RESIZABLE)

    def click(self, position):
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position)
        self.game.step(1 / 60, [event], position)

    def test_menu_to_game_exit_modal_pause_and_second_session(self):
        self.click((480, 270))
        self.assertEqual(self.game.page, 'session')
        self.click((480, 260))
        self.assertEqual(self.game.page, 'playing')
        popup = next(e for e in self.game.session.events.events_all if e['id'] == 'phone_doomscroll')
        self.game.session.events._begin_event(popup)
        self.click((30, 520))
        self.assertTrue(self.game.exit_dialog_open)
        before = self.game.session.stats.copy()
        elapsed = self.game.session.events._elapsed
        self.game.step(0.1, [], (0, 0))
        self.assertEqual(self.game.session.stats, before)
        self.assertEqual(self.game.session.events._elapsed, elapsed)
        self.assertIsNotNone(self.game.session.events.current_event)
        confirm, _ = ui.draw_exit_confirm_dialog(self.game.canvas, (0, 0))
        self.click(confirm.center)
        self.assertEqual(self.game.page, 'start')
        self.click((480, 270))
        self.click((480, 260))
        self.assertEqual(self.game.session.stats['progress'], 0)
        self.assertIs(self.game.session.events.stats, self.game.session.stats)

    def test_choice_buttons_are_visible_in_both_languages(self):
        for language in ('en', 'zh'):
            ui.set_lang(language)
            set_lang(language)
            for event in self.game.session.events.events_all:
                if event.get('choices'):
                    with self.subTest(language=language, event=event['id']):
                        buttons = ui.draw_event_dialog(self.game.canvas, event, (0, 0))
                        self.assertEqual(len(buttons), len(event['choices']))
                        for rect in buttons:
                            self.assertTrue(self.game.canvas.get_rect().contains(rect))
                        for first, second in zip(buttons, buttons[1:]):
                            self.assertFalse(first.colliderect(second))
        ui.set_lang(self.game.lang)
        set_lang(self.game.lang)

    def test_letterbox_mouse_mapping_and_tiny_window_render(self):
        resize = pygame.event.Event(pygame.VIDEORESIZE, w=1200, h=540)
        self.game.step(0, [resize], (0, 0))
        self.assertEqual(self.game.logical_mouse((600, 270)), (480, 270))
        self.assertEqual(self.game.logical_mouse((10, 10)), (-1000, -1000))
        self.click((600, 270))
        self.assertEqual(self.game.page, 'session')
        resize = pygame.event.Event(pygame.VIDEORESIZE, w=100, h=70)
        self.game.step(0, [resize], (0, 0))
        self.assertEqual(self.game.screen.get_size(), (100, 70))

    def test_done_render_and_escape_are_available(self):
        self.game.session.start(0)
        self.game.page = 'playing'
        self.game.session.stats['progress'] = 100
        self.game.step(0, [], (0, 0))
        self.assertEqual(self.game.session.state.domain, 'done')
        self.game.step(0, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)], (0, 0))
        self.assertTrue(self.game.exit_dialog_open)


if __name__ == '__main__':
    unittest.main()
