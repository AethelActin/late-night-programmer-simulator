"""基于游戏时间的双层事件调度；模板与每次弹窗的运行状态分离。"""

import json
import random
import re

from src.config import resource_path


class EventSystem:
    def __init__(self, events_path: str, ambient_path: str, stats: dict):
        self.events_all = self._load(resource_path(events_path))
        self.ambient_pool = self._load(resource_path(ambient_path))
        self.stats = stats
        self._on_trigger = None
        self._on_end = None
        self._on_world_change = None
        self._extra_filter = None
        self._rain_stops_cached = next(
            (e for e in self.events_all if e['id'] == 'rain_stops'), None
        )
        self.reset()

    @staticmethod
    def _load(path: str) -> list:
        with open(path, encoding='utf-8') as source:
            content = re.sub(r'^\s*//.*$', '', source.read(), flags=re.MULTILINE)
        raw = json.loads(content)
        events = raw['events'] if isinstance(raw, dict) else raw
        for event in events:
            effects = event.setdefault('effects', {})
            if 'sanity' in event:
                effects['reality'] = event.pop('sanity')
            req = event.setdefault('requirements', {})
            if 'sanity_max' in event:
                req['reality_max'] = event.pop('sanity_max')
            for item in [event, *event.get('choices', [])]:
                item_effects = item.get('effects', {})
                if 'sanity' in item_effects:
                    item_effects['reality'] = item_effects.pop('sanity')
            if 'sanity_max' in req:
                req['reality_max'] = req.pop('sanity_max')
            event.setdefault('animation', None)
            event.setdefault('severity', 'major' if event.get('animation') or event.get('choices') else 'ambient')
        return events

    def reset(self):
        """保留回调、模板与 stats 引用，清空上一局全部运行状态。"""
        self.current_event = None
        self.ambient_log = []
        self._elapsed = 0.0
        self._major_remaining = random.uniform(12, 22)
        self._ambient_remaining = random.uniform(5, 8)
        self._auto_dismiss_timer = 0.0
        self._auto_dismiss_duration = 8.0
        self._rain_start_time = None

    def reset_major_cooldown(self):
        self._major_remaining = 0.0

    def clear_current_event(self):
        """结局切换时丢弃旧弹窗，不能继续应用上一场景的效果。"""
        self.current_event = None
        self._auto_dismiss_timer = 0.0

    def set_extra_filter(self, filter_fn):
        self._extra_filter = filter_fn

    def set_callbacks(self, on_trigger, on_end, on_world_change=None):
        self._on_trigger = on_trigger
        self._on_end = on_end
        self._on_world_change = on_world_change

    def update(self, dt: float):
        dt = max(0.0, dt)
        self._elapsed += dt
        self._ambient_remaining -= dt
        if self.current_event is not None:
            self._auto_dismiss_timer += dt
            # 无人操作依然可以游玩；有选项的事件超时中性关闭，不能代选。
            if self._auto_dismiss_timer >= self._auto_dismiss_duration:
                self.dismiss_event(skip_effects=bool(self.current_event.get('choices')))
            return

        domain = self.stats.get('world_state', 'no_rain')
        if (domain == 'rain' and self._rain_start_time is not None
                and self._elapsed - self._rain_start_time >= 60
                and self._rain_stops_cached and self._allowed(self._rain_stops_cached)):
            self._begin_event(self._rain_stops_cached)
            return

        if domain != 'done' and self._ambient_remaining <= 0:
            available = self._get_available_ambient()
            if available:
                event = self._pick(available)
                self.ambient_log.append(event)
                del self.ambient_log[:-6]
                self._apply(event.get('effects', {}))
            self._ambient_remaining = random.uniform(5, 8)

        self._major_remaining -= dt
        if self._major_remaining <= 0:
            candidates = [e for e in self._get_available_events() if e['severity'] == 'major']
            if candidates:
                self._begin_event(self._pick(candidates))

    def _begin_event(self, event):
        self.current_event = dict(event)
        self._auto_dismiss_timer = 0.0
        # 域切换与动画同一时刻发生，不能等弹窗关闭后才开始下雨/雨停。
        effects = event.get('effects', {})
        if 'world_state' in effects:
            self._apply({'world_state': effects['world_state']})
        if self._on_trigger:
            self._on_trigger(self.current_event)

    def _allowed(self, event):
        domain = self.stats.get('world_state', 'no_rain')
        ed = event.get('domain', 'both')
        if ed not in ('both', domain) or (domain == 'done' and ed != 'done'):
            return False
        if event.get('id') == 'rain_stops':
            if self._rain_start_time is None or self._elapsed - self._rain_start_time < 30:
                return False
        req = event.get('requirements', {})
        if 'reality_max' in req and self.stats.get('reality', 100) > req['reality_max']:
            return False
        if any(self.stats.get(key, 0) < req[name] for key, name in
               [('vibe', 'vibe_min'), ('progress', 'progress_min')] if name in req):
            return False
        return not self._extra_filter or self._extra_filter(event, {})

    def _get_available_events(self):
        return [e for e in self.events_all if self._allowed(e)]

    def _get_available_ambient(self):
        if self.stats.get('world_state') == 'done':
            return []
        # events.json 中未带动画/选项的条目原先既不弹窗，也不进日志。
        pool = self.ambient_pool + [e for e in self.events_all if e['severity'] == 'ambient']
        return [e for e in pool if self._allowed(e)]

    @staticmethod
    def _pick(events):
        return random.choices(events, weights=[e.get('weight', 10) for e in events], k=1)[0]

    def choose_option(self, option_index: int):
        """一次选择原子化结算并关闭，避免重复点击叠加效果。"""
        if not self.current_event:
            return False
        choices = self.current_event.get('choices', [])
        if not 0 <= option_index < len(choices):
            return False
        self._apply(choices[option_index].get('effects', {}))
        self._end_event(user_dismiss=True)
        return True

    def dismiss_event(self, skip_effects=False):
        if not self.current_event:
            return
        if not skip_effects:
            effects = {k: v for k, v in self.current_event.get('effects', {}).items() if k != 'world_state'}
            self._apply(effects)
        self._end_event(user_dismiss=True)

    def _apply(self, effects):
        for key, value in effects.items():
            if key in ('vibe', 'reality', 'progress'):
                self.stats[key] = max(0, min(100, self.stats.get(key, 50) + value))
            elif key == 'world_state':
                # sunrise 是剧情标记，没有独立动画域，继续沿用当前场景。
                if value not in ('no_rain', 'rain', 'done'):
                    continue
                old = self.stats.get(key, 'no_rain')
                self.stats[key] = value
                if value != old:
                    self._rain_start_time = self._elapsed if value == 'rain' else None
                    if self._on_world_change:
                        self._on_world_change(value)

    def _end_event(self, user_dismiss=False):
        event = self.current_event
        self.clear_current_event()
        self._major_remaining = random.uniform(12, 22)
        if self._on_end:
            self._on_end(event, user_dismiss)

    def is_waiting_animation(self):
        return bool(self.current_event and self.current_event.get('_wait_animation'))
