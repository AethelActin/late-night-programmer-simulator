import os
import sys


def resource_path(path: str) -> str:
    """pyinstaller 打包后用 _MEIPASS 找资源"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, path)


# 窗口
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FPS = 60
SESSION_SPEEDS = ((0.15, 0.3), (0.08, 0.25), (0.01, 0.03))

# 素材原生分辨率
SPRITE_NATIVE_WIDTH = 1280
SPRITE_NATIVE_HEIGHT = 720

# 帧序列
SPRITE_DIR = resource_path("assets/images/sprites")
DEFAULT_FPS = 8

# 色调映射阈值
VIBE_HIGH_THRESHOLD = 70
VIBE_LOW_THRESHOLD = 30

# 状态初始值
INITIAL_STATS = {
    "vibe": 30,
    "reality": 60,
    "progress": 0,
}

# 事件
EVENT_COOLDOWN_MIN = 8.0
EVENT_COOLDOWN_MAX = 15.0
PROGRESS_PER_SECOND = 0.25
PROGRESS_MAX = 100

# UI
PANEL_X = 10
PANEL_Y = 10
PANEL_WIDTH = 220
PANEL_HEIGHT = 120
TOAST_DURATION = 3.5
COZY_HINT_DURATION = 1.0
