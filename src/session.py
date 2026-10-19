"""一局游戏的状态和联动，不依赖菜单布局或窗口大小。"""

from src.config import INITIAL_STATS, PROGRESS_MAX, SESSION_SPEEDS
from src.event_system import EventSystem
from src.state_manager import StateManager


class GameSession:
    def __init__(self, sprite_player):
        self.sprite = sprite_player
        self.stats = {}
        self.state = StateManager(self._transition)
        self.events = EventSystem('data/events.json', 'data/ambient.json', self.stats)
        self.events.set_callbacks(self._on_event, None, self._world_change)
        self.events.set_extra_filter(self._event_allowed)
        self.reset()

    def _transition(self, name, transition, loop):
        self.sprite.play(name, transition)
        self.sprite.loop = loop

    def reset(self):
        # 原地重置，确保事件系统与 UI 始终看到同一个字典。
        self.stats.clear()
        self.stats.update(INITIAL_STATS)
        self.stats.update(world_state='no_rain', _compile_dots=0)
        self.events.reset()
        self.state.reset()

    def start(self, session_index):
        self.reset()
        self.stats['_reality_speed'], self.stats['_progress_speed'] = SESSION_SPEEDS[session_index]

    def _world_change(self, domain):
        self.state.domain = domain

    def _on_event(self, event):
        animation = event.get('animation')
        if animation:
            self.state.request_animation(animation)
            event['_wait_animation'] = not event.get('choices') and animation != 'rain_stop'
            if event['id'] == 'cat_on_keyboard':
                self.state.set_animation_chain([
                    ('cat_type_remove', 'direct'), ('cat_down', 'direct')
                ])

    def _event_allowed(self, event, context):
        if self.state.is_chain_active:
            return False
        if event['id'] == 'cat_stare':
            return self.state.current_animation in ('cat_wake', 'rain_cat_wake', 'rain_cat_watch')
        if event['id'] == 'rain_cat_wakes':
            return self.state.current_animation not in ('rain_cat_wake', 'rain_cat_watch')
        return True

    def _finish_if_needed(self):
        if self.state.domain == 'done':
            return
        if self.stats['reality'] > 0 and self.stats['progress'] < PROGRESS_MAX:
            return
        self.stats['_done_reason'] = 'sanity' if self.stats['reality'] <= 0 else 'progress'
        self.events.clear_current_event()
        self.events.ambient_log.clear()
        self.events.reset_major_cooldown()
        self.state.request_animation('done')
        self.stats['world_state'] = 'done'

    def update(self, dt):
        if self.state.domain != 'done':
            self.stats['progress'] = min(PROGRESS_MAX, self.stats['progress'] + self.stats['_progress_speed'] * dt)
            self.stats['reality'] = max(0, self.stats['reality'] - self.stats['_reality_speed'] * dt)
        self._finish_if_needed()
        self.sprite.update(dt)
        self.state.update(dt)
        if self.sprite.is_finished() and self.state.domain != 'done':
            self.state.on_animation_finished()

        current = self.events.current_event
        if (current and current.get('_wait_animation') and not self.state.is_chain_active
                and self.state.current_animation != current.get('animation')):
            self.events.dismiss_event()

        if self.stats.get('_done_reason') != 'sanity':
            self.events.update(dt)
        # 日志效果也可能让进度达到上限；同帧进入结局。
        self._finish_if_needed()
