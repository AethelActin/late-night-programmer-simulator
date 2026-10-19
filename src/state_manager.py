import random
from typing import Callable

# 模糊转场动画列表（使用 fade 过渡）
FADE_ANIMATIONS = {
    "drink", "drowsy", "excited", "phone",
    "rain", "rain_cat_wake", "rain_cat_watch",
    "rain_idle", "scratch",
}


class StateManager:
    """状态机，管理精灵动画的领域切换与转场规则"""

    def __init__(self, on_transition: Callable[[str, str | None, bool], None]):
        """
        :param on_transition: 回调函数，接收 (动画名, 过渡方式, 是否循环)
        """
        self.domain = "no_rain"  # "no_rain" | "rain" | "done"
        self.current_animation = "idle1"
        self.idle_pool = ["idle1", "idle2", "idle3"]
        self._idle_weights = [8, 2, 1]  # idle1 为主，idle2 中等，idle3（打哈欠）最低
        self._on_transition = on_transition
        self._idle_timer = 0.0
        self._idle_interval = random.uniform(5, 8)
        self._animation_chain: list[tuple[str, str | None]] = []  # 自动动画链
        self._chain_locked = False  # 动画链播放中时锁定，不接受新事件
        self._cat_watch_timer = 0.0  # rain_cat_watch 计时器

    def set_animation_chain(self, chain: list[tuple[str, str | None]]):
        """播放完当前动画后自动播放下一个"""
        self._animation_chain = list(chain)
        self._chain_locked = bool(chain)

    def reset(self):
        """开始新一局，清除上一局领域、动画链及定时器。"""
        self.domain = "no_rain"
        self._animation_chain.clear()
        self._chain_locked = False
        self._idle_timer = 0.0
        self._idle_interval = random.uniform(5, 8)
        self._cat_watch_timer = 0.0
        self._play("idle1", None)

    @property
    def is_chain_active(self) -> bool:
        """动画链是否正在播放中"""
        return self._chain_locked

    def update(self, dt: float):
        """每帧更新定时器"""
        # rain_cat_watch 15 秒后自动转 rain_idle
        if self.domain == "rain" and self.current_animation == "rain_cat_watch":
            self._cat_watch_timer += dt
            if self._cat_watch_timer >= 15.0:
                self._cat_watch_timer = 0.0
                self._play("rain_idle", "fade")
            return

        if self.domain != "no_rain":
            return
        if self.current_animation not in ("idle1", "idle2", "idle3"):
            return
        self._idle_timer += dt
        if self._idle_timer >= self._idle_interval:
            self._idle_timer = 0.0
            self._idle_interval = random.uniform(5, 8)
            # idle2/idle3 播完一次后必须回 idle1
            if self.current_animation in ("idle2", "idle3"):
                self._play("idle1", None)
            else:
                self._play_random_idle()

    def request_animation(self, name: str):
        """外部请求播放指定动画"""
        if name == "done":
            if self.domain == "done":
                return
            self._animation_chain.clear()
            self._chain_locked = False
            self.domain = "done"
            self._play("done", "fade")
            return

        # 胜利出口可打断动画链；结局开始后忽略普通事件。
        if self._chain_locked or self.domain == "done":
            return

        if name == "rain":
            self.domain = "rain"
            self._cat_watch_timer = 0.0  # 重置猫观察计时器
            self._play("rain", "fade")
            return

        if name == "rain_stop":
            # 雨停：fade 到 idle1，由事件 effects 切 domain
            self._cat_watch_timer = 0.0
            self._play("idle1", "fade")
            return

        # rain_idle 时不能直接转非 rain 域动画
        if self.current_animation == "rain_idle" and name not in ("rain_cat_wake", "idle1", "idle2", "idle3"):
            return

        if self.current_animation == "rain_idle" and name == "rain_cat_wake":
            self._play(name, "fade")
            return

        # 进入动画一律直接切换（退出时由 on_animation_finished 决定是否 fade）
        self._play(name, None)

    def on_animation_finished(self):
        """非循环动画播完后自动回到对应的空闲动画"""
        # 优先检查动画链
        if self._animation_chain:
            next_anim = self._animation_chain.pop(0)
            self._play(next_anim[0], next_anim[1])
            return

        # 最后一段动画也完整播完后才解锁。
        self._chain_locked = False

        if self.domain == "no_rain":
            # 非 idle 动画播完后回 idle，当前动画在模糊列表中则 fade 退出
            fade_out = self.current_animation in FADE_ANIMATIONS
            trans = "fade" if fade_out else None
            self._play_random_idle(trans)
        elif self.domain == "rain":
            if self.current_animation == "rain_cat_wake":
                self._cat_watch_timer = 0.0
                self._play("rain_cat_watch", "direct")
            elif self.current_animation == "rain":
                # rain 播完不自动跳，由事件系统触发 rain_cat_wakes
                self._play("rain_idle", "fade")
            else:
                fade_out = self.current_animation in FADE_ANIMATIONS
                trans = "fade" if fade_out else None
                self._play("rain_idle", trans)
        # done 领域不自动切换，保持最后一帧

    def request_random_idle(self):
        """手动切换到随机空闲动画"""
        self._play_random_idle(None)

    def _play(self, name: str, transition: str | None):
        """内部播放方法，设置当前动画并触发回调"""
        self.current_animation = name
        # 循环动画列表
        loop = name in ["idle1", "idle2", "idle3", "rain_idle", "rain_cat_watch"]
        self._on_transition(name, transition, loop)

    def _play_random_idle(self, trans: str | None = None):
        """从空闲池中加权随机选取一个播放"""
        target = random.choices(self.idle_pool, weights=self._idle_weights, k=1)[0]
        self._play(target, trans)
