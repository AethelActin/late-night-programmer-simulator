import pygame
import os
import glob
from collections import OrderedDict


class SpritePlayer:
    """帧序列加载与播放器，支持 fade 转场"""

    def __init__(self):
        self.sequences: dict[str, list[pygame.Surface]] = {}
        self.current_seq: str | None = None
        self.frame_index = 0
        self.loop = False
        self.fps = 8
        self._timer = 0.0
        self._finished = False
        self._sequence_loops: dict[str, bool] = {}
        self._sequence_files: dict[str, list[str]] = {}
        self._frame_cache: OrderedDict[tuple[str, int], pygame.Surface] = OrderedDict()
        self.max_cached_frames = 96

        # 转场状态
        self.transition: str | None = None  # "fade" or None
        self.transition_progress = 0.0
        self.old_frame: pygame.Surface | None = None
        self.transition_duration = 1.5  # 秒（柔和过渡）
        self._black_screen = None

    def load_sequence(self, name: str, folder_path: str, loop: bool = False):
        """从文件夹加载 PNG 帧序列"""
        pattern = os.path.join(folder_path, "*.png")
        files = sorted(glob.glob(pattern))
        if not files:
            raise ValueError(f"动画 {name!r} 没有 PNG 帧：{folder_path}")
        # 仅注册路径；全部帧预解码会占用数 GiB 内存。
        self._sequence_files[name] = files
        self.sequences.pop(name, None)
        for key in list(self._frame_cache):
            if key[0] == name:
                del self._frame_cache[key]
        self._sequence_loops[name] = loop

    def _frame_count(self, name: str | None) -> int:
        if name in self.sequences:
            return len(self.sequences[name])
        return len(self._sequence_files.get(name, ()))

    def _get_sequence_frame(self, name: str, index: int) -> pygame.Surface:
        # 手工 Surface 列表仍可供调用方和单元测试使用。
        if name in self.sequences:
            return self.sequences[name][index]
        key = (name, index)
        if key in self._frame_cache:
            self._frame_cache.move_to_end(key)
            return self._frame_cache[key]
        # 逐帧解码：长动画切换不再一次加载数十张图片。
        while len(self._frame_cache) >= self.max_cached_frames:
            self._frame_cache.popitem(last=False)
        frame = pygame.image.load(self._sequence_files[name][index]).convert_alpha()
        self._frame_cache[key] = frame
        return frame

    def play(self, name: str, transition: str | None = None):
        """切换到指定动画"""
        if not self._frame_count(name):
            raise ValueError(f"动画 {name!r} 未加载或没有帧")
        previous_frame = self.get_frame() if transition == "fade" else None
        # 缓存淘汰前保留当前画面的单帧，而非整条旧序列。
        previous_frame = previous_frame.copy() if previous_frame is not None else None
        if transition == "fade" and previous_frame is not None:
            self.old_frame = previous_frame
            self.transition = "fade"
            self.transition_progress = 0.0
        else:
            self.old_frame = None
            self.transition = None
            self.transition_progress = 1.0

        self.current_seq = name
        self.frame_index = 0
        self._timer = 0.0
        self._finished = False
        self.loop = self._sequence_loops.get(name, False)

    def update(self, dt: float):
        """推进帧索引或转场进度"""
        frame_count = self._frame_count(self.current_seq)
        if not frame_count or self._finished:
            return

        # 推进转场
        if self.transition:
            self.transition_progress += dt / self.transition_duration
            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.transition = None
                self.old_frame = None
                self._black_screen = None
            return

        # 推进帧
        self._timer += dt
        frame_duration = 1.0 / self.fps
        while self._timer >= frame_duration:
            self._timer -= frame_duration
            self.frame_index += 1
            if self.frame_index >= frame_count:
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = frame_count - 1
                    self._finished = True
                    self._timer = 0.0
                    break

    def get_frame(self) -> pygame.Surface | None:
        """返回当前应渲染的帧"""
        if not self._frame_count(self.current_seq):
            return None

        if self.transition:
            # 真正的交叉淡入淡出：old_frame 透明度渐降 + 新帧透明度渐升
            # 整个过渡持续 transition_duration（目前 1.5s）
            t = self.transition_progress
            if self.old_frame:
                # 前半段：old_frame 逐渐透明 + 新帧逐渐显现
                result = self.old_frame.copy()
                # new_frame 的 alpha 从 0 升到 255
                new_frame = self._get_sequence_frame(self.current_seq, 0).copy()
                new_frame.set_alpha(int(255 * t))
                result.blit(new_frame, (0, 0))
                return result
            else:
                # 没有 old_frame 时新帧直接淡入
                result = self._get_sequence_frame(self.current_seq, 0).copy()
                result.set_alpha(int(255 * t))
                return result

        return self._get_sequence_frame(self.current_seq, self.frame_index)

    def is_finished(self) -> bool:
        """非循环序列是否播完"""
        return self._finished and not self.loop
