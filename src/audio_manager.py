import pygame
import os
import random
import glob

from src.config import resource_path

AUDIO_DIR = resource_path(os.path.join("assets", "audio"))

DOMAIN_FOLDERS = {
    "no_rain": "no_rain_loop",
    "rain": "rain_loop",
    "done": "done_loop",
}

FADE_DURATION = 2.0


class AudioManager:
    """背景音乐管理器，交叉淡出切换（旧歌渐弱、新歌渐强）"""

    def __init__(self):
        self._enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self._enabled = True
        except pygame.error:
            # 无声卡、远程桌面等环境仍可游玩。
            pass
        self._current_domain: str | None = None
        # 两个 channel：一个播旧的（淡出），一个播新的（淡入）
        self._ch_a = pygame.mixer.Channel(0) if self._enabled else None
        self._ch_b = pygame.mixer.Channel(1) if self._enabled else None
        self._active_ch = self._ch_a  # 当前主 channel
        self._volume = 0.4
        self._muted = False
        self._fading = False
        self._fade_timer = 0.0
        self._next_domain: str | None = None
        self._old_ch = None
        self._old_start_gain = 1.0
        self._playlists: dict[str, list[str]] = {}
        if self._enabled:
            self._load_all()

    def _load_all(self):
        if not os.path.isdir(AUDIO_DIR):
            return
        for folder in os.listdir(AUDIO_DIR):
            path = os.path.join(AUDIO_DIR, folder)
            if not os.path.isdir(path):
                continue
            domain = None
            for key, val in DOMAIN_FOLDERS.items():
                if val == folder:
                    domain = key
                    break
            if domain is None and folder == "low_reality_loop":
                domain = "low_reality"
            if domain is None:
                continue
            files = sorted(glob.glob(os.path.join(path, "*.mp3")))
            if files:
                # 只保存路径；交叉淡入时才解码选中的一首。
                self._playlists[domain] = files

    def set_volume(self, vol: float):
        self._volume = max(0.0, min(1.0, vol))
        self._apply_volumes()

    @property
    def muted(self) -> bool:
        return self._muted

    @property
    def has_music(self) -> bool:
        return any(self._playlists.values())

    def toggle_mute(self):
        """切换静音状态，关闭/恢复所有音乐"""
        self._muted = not self._muted
        self._apply_volumes()

    def _apply_volumes(self):
        if not self._enabled:
            return
        vol = 0.0 if self._muted else self._volume
        t = min(1.0, self._fade_timer / FADE_DURATION) if self._fading else 1.0
        self._active_ch.set_volume(vol * t)
        other = self._ch_b if self._active_ch == self._ch_a else self._ch_a
        other.set_volume(vol * (1.0 - t) * self._old_start_gain if self._fading else 0.0)

    def update(self, domain: str, reality: float, dt: float):
        if not self._enabled:
            return
        if domain == "done":
            target = "done"
        elif reality <= 20:
            target = "low_reality"
        elif domain in DOMAIN_FOLDERS:
            target = domain
        else:
            target = "no_rain"

        playing_target = self._next_domain if self._fading else self._current_domain
        if target != playing_target:
            self._start_crossfade(target)

        if self._fading:
            self._tick_fade(dt)

    def _start_crossfade(self, target: str):
        """开始交叉淡出：旧歌渐弱，新歌渐强"""
        sounds = self._playlists.get(target)
        if not sounds:
            return
        # 损坏或不支持的音频不应导致游戏退出，也不保留解码失败的条目。
        sound = None
        while sounds:
            candidate = random.choice(sounds)
            try:
                sound = pygame.mixer.Sound(candidate)
                break
            except (pygame.error, OSError):
                sounds.remove(candidate)
        if sound is None:
            return

        # 切换主 channel
        old_ch = self._active_ch
        new_ch = self._ch_b if self._active_ch == self._ch_a else self._ch_a
        self._old_start_gain = min(1.0, self._fade_timer / FADE_DURATION) if self._fading else 1.0

        # 新 channel 播新歌
        new_ch.stop()
        new_ch.play(sound, -1)
        new_ch.set_volume(0.0)

        self._active_ch = new_ch
        self._old_ch = old_ch
        self._next_domain = target
        self._fading = True
        self._fade_timer = 0.0
        self._apply_volumes()

    def _tick_fade(self, dt: float):
        self._fade_timer += max(0.0, dt)
        t = min(1.0, self._fade_timer / FADE_DURATION)

        # 新歌渐强，旧歌渐弱
        self._apply_volumes()

        if t >= 1.0:
            # 淡出完成，停掉旧 channel
            if self._old_ch is not None:
                self._old_ch.stop()
            self._current_domain = self._next_domain
            self._fading = False
            self._apply_volumes()

    def stop(self):
        if self._enabled:
            self._ch_a.stop()
            self._ch_b.stop()
        self._current_domain = None
        self._next_domain = None
        self._fading = False
        self._fade_timer = 0.0
        self._old_ch = None
