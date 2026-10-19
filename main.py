"""桌面入口：窗口、菜单和输入。局内规则见 src/session.py。"""

import os
import argparse

import pygame

from src import ui
from src.audio_manager import AudioManager
from src.config import FPS, SPRITE_DIR, WINDOW_HEIGHT, WINDOW_WIDTH
from src.font_manager import get_font, set_lang as font_set_lang
from src.session import GameSession
from src.sprite_engine import SpritePlayer
from src.metadata import TITLE_EN, TITLE_ZH


def load_all_sequences(player):
    """注册素材路径；播放时才解码，避免启动时加载全部 662 帧。"""
    for folder in sorted(os.listdir(SPRITE_DIR)):
        path = os.path.join(SPRITE_DIR, folder)
        if os.path.isdir(path):
            player.load_sequence(folder, path)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE_ZH)
        self.canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.fill((20, 24, 30))
        pygame.display.flip()
        player = SpritePlayer()
        load_all_sequences(player)
        self.session = GameSession(player)
        self.audio = AudioManager()
        self.audio.set_volume(0.35)
        self.page = 'start'
        self.lang = 'zh'
        ui.set_lang(self.lang)
        font_set_lang(self.lang)
        self.exit_dialog_open = False
        self.running = True
        self.dialog_fade = {'event': None, 'timer': 0.0}
        self.session.events.set_callbacks(self.session._on_event, self._event_closed, self.session._world_change)

    def _event_closed(self, event, user_dismiss=False):
        self.dialog_fade = {'event': event, 'timer': 0.4}

    def _return_to_menu(self):
        self.session.reset()
        self.page = 'start'
        self.exit_dialog_open = False
        self.dialog_fade = {'event': None, 'timer': 0.0}
        ui.set_lang(self.lang)

    def viewport(self):
        width, height = self.screen.get_size()
        scale = min(width / WINDOW_WIDTH, height / WINDOW_HEIGHT)
        size = (max(1, int(WINDOW_WIDTH * scale)), max(1, int(WINDOW_HEIGHT * scale)))
        return pygame.Rect((width - size[0]) // 2, (height - size[1]) // 2, *size)

    def logical_mouse(self, position):
        viewport = self.viewport()
        if not viewport.collidepoint(position):
            return (-1000, -1000)
        return ((position[0] - viewport.x) * WINDOW_WIDTH / viewport.w,
                (position[1] - viewport.y) * WINDOW_HEIGHT / viewport.h)

    def step(self, dt, events, mouse_position):
        # 局内使用游戏时间；挂起恢复不让数分钟墙钟时间吞掉整局。
        dt = max(0.0, min(dt, 0.1))
        clicked = False
        key_pressed = False
        escape = False
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((max(1, event.w), max(1, event.h)), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
                mouse_position = event.pos
            elif event.type == pygame.KEYDOWN:
                escape = event.key == pygame.K_ESCAPE
                key_pressed = event.key != pygame.K_ESCAPE
        mouse = self.logical_mouse(mouse_position)
        if not self.running:
            return

        if self.page != 'playing':
            self.session.sprite.update(dt)
            if escape:
                self.page = 'start'
            self._draw_background()
            if self.page == 'start':
                buttons, language, music = ui.draw_start_screen(
                    self.canvas, mouse, self.audio.muted, self.audio.has_music)
                if clicked:
                    if buttons[0].collidepoint(mouse):
                        self.page = 'session'
                    elif buttons[1].collidepoint(mouse):
                        self.page = 'howtoplay'
                    elif buttons[2].collidepoint(mouse):
                        self.running = False
                    elif language.collidepoint(mouse):
                        self.lang = 'en' if self.lang == 'zh' else 'zh'
                        ui.set_lang(self.lang)
                        font_set_lang(self.lang)
                        pygame.display.set_caption(TITLE_ZH if self.lang == 'zh' else TITLE_EN)
                    elif self.audio.has_music and music.collidepoint(mouse):
                        self.audio.toggle_mute()
            elif self.page == 'session':
                buttons = ui.draw_session_screen(self.canvas, mouse)
                if clicked:
                    for index, rect in enumerate(buttons):
                        if rect.collidepoint(mouse):
                            if index < 3:
                                self.session.start(index)
                                self.page = 'playing'
                            else:
                                self.page = 'start'
                            break
            elif self.page == 'howtoplay':
                back = ui.draw_how_to_play_screen(self.canvas, mouse)
                if clicked and back.collidepoint(mouse):
                    self.page = 'start'
        else:
            # 先分派模态输入；打开确认框的一次点击不会同时关闭事件。
            if escape:
                self.exit_dialog_open = not self.exit_dialog_open
                clicked = key_pressed = False
            if not self.exit_dialog_open:
                exit_rect = ui.draw_exit_button(self.canvas, mouse)
                if clicked and exit_rect.collidepoint(mouse):
                    self.exit_dialog_open = True
                    clicked = key_pressed = False
            paused = self.exit_dialog_open
            if not paused:
                self.session.update(dt)
                if self.session.state.domain == 'done':
                    self.dialog_fade = {'event': None, 'timer': 0.0}
            self._draw_background()
            ui.apply_vibe_tint(self.canvas, self.session.stats['vibe'])
            ui.draw_status_panel(self.canvas, self.session.stats, 0 if paused else dt,
                                 self.session.state.domain == 'done')
            current = self.session.events.current_event
            if current:
                buttons = ui.draw_event_dialog(self.canvas, current, mouse)
                if not paused:
                    if current.get('choices'):
                        if clicked:
                            for index, rect in enumerate(buttons):
                                if rect.collidepoint(mouse):
                                    self.session.events.choose_option(index)
                                    break
                    elif clicked or key_pressed:
                        self.session.events.dismiss_event()
            fade = self.dialog_fade
            if fade['event'] and fade['timer'] > 0 and not self.session.events.current_event:
                if not paused:
                    fade['timer'] = max(0, fade['timer'] - dt)
                ui.draw_event_dialog(self.canvas, fade['event'], mouse, int(255 * fade['timer'] / 0.4))
            ui.draw_ambient_log(self.canvas, self.session.events.ambient_log, self.session.stats['vibe'])
            self._draw_result()
            ui.draw_exit_button(self.canvas, mouse)
            if paused:
                confirm, cancel = ui.draw_exit_confirm_dialog(self.canvas, mouse)
                if clicked and confirm.collidepoint(mouse):
                    self._return_to_menu()
                elif clicked and cancel.collidepoint(mouse):
                    self.exit_dialog_open = False
        domain = self.session.state.domain if self.page == 'playing' else 'no_rain'
        reality = self.session.stats['reality'] if self.page == 'playing' else 60
        self.audio.update(domain, reality, dt)
        self._present()

    def _draw_background(self):
        frame = self.session.sprite.get_frame()
        if frame is None:
            self.canvas.fill((20, 24, 30))
        else:
            self.canvas.blit(pygame.transform.scale(frame, self.canvas.get_size()), (0, 0))
        # 原版有意遮住 AI 动画右下角的可见水印；在逻辑画布上随窗口等比缩放。
        width, height = self.canvas.get_size()
        cover_width, cover_height = max(60, width // 16), max(40, height // 14)
        pygame.draw.rect(self.canvas, (10, 12, 16),
                         (width - cover_width - 4, height - cover_height,
                          cover_width, cover_height))

    def _draw_result(self):
        reason = self.session.stats.get('_done_reason')
        if not reason:
            return
        if self.lang == 'zh':
            message = '天快亮了。休息一下吧。' if reason == 'sanity' else '项目编译完成。今晚辛苦了。'
            message += '  按 Esc 返回菜单'
        else:
            message = 'Time to rest.' if reason == 'sanity' else 'Project complete. Good work tonight.'
            message += '  Esc: menu'
        surface = get_font(12).render(message, True, (190, 200, 210))
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        pygame.draw.rect(self.canvas, (10, 12, 16), rect.inflate(20, 12))
        self.canvas.blit(surface, rect)

    def _present(self):
        viewport = self.viewport()
        self.screen.fill((10, 12, 16))
        self.screen.blit(pygame.transform.scale(self.canvas, viewport.size), viewport)
        pygame.display.flip()

    def close(self):
        self.audio.stop()
        pygame.quit()


def smoke_test(game):
    """供构建后离屏验证使用；加载真实素材并走菜单、两种结局和重开。"""
    def click(position):
        game.step(0, [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position)], position)

    game.step(0, [], (0, 0))
    click((480, 270))
    click((480, 260))
    assert game.page == 'playing'
    game.session.stats['reality'] = 0
    game.step(0, [], (0, 0))
    assert game.session.stats['_done_reason'] == 'sanity'
    game._return_to_menu()
    click((480, 270))
    click((480, 260))
    game.session.stats['progress'] = 100
    game.step(0, [], (0, 0))
    assert game.session.state.domain == 'done'
    assert game.session.events.current_event['domain'] == 'done'
    game.step(0, [pygame.event.Event(pygame.QUIT)], (0, 0))
    assert not game.running


def main():
    parser = argparse.ArgumentParser(description=TITLE_EN)
    parser.add_argument('--smoke-test', action='store_true', help='run a short local packaging check and exit')
    args = parser.parse_args()
    game = None
    try:
        game = Game()
        if args.smoke_test:
            smoke_test(game)
            return
        clock = pygame.time.Clock()
        while game.running:
            game.step(clock.tick(FPS) / 1000.0, pygame.event.get(), pygame.mouse.get_pos())
    finally:
        if game:
            game.close()
        else:
            pygame.quit()


if __name__ == '__main__':
    main()
