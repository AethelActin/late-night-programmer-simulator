import pygame
import os

from src.config import resource_path

FONT_EN = resource_path(os.path.join("assets", "fonts", "PressStart2P-Regular.ttf"))
FONT_ZH = resource_path(os.path.join("assets", "fonts", "FusionPixel10.ttf"))

_font_cache = {}
_current_lang = "en"  # "en" 或 "zh"


class _BoldFontWrapper:
    """中文像素字体模拟粗体的封装层，自动做水平偏移叠加"""

    def __init__(self, font: pygame.font.Font):
        self._font = font

    def render(self, text: str, antialias: bool, color: tuple,
               bgcolor: tuple | None = None) -> pygame.Surface:
        base = self._font.render(text, antialias, color, bgcolor)
        if _current_lang != "zh":
            return base
        # 水平偏移 1px 叠加模拟粗体（仅右移 1px，不重叠三层以免过粗）
        surf = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        for dx in (0, 1):
            surf.blit(base, (dx, 0))
        surf.set_colorkey((0, 0, 0, 0))
        return surf

    def size(self, text: str) -> tuple:
        return self._font.size(text)

    def get_height(self) -> int:
        return self._font.get_height()

    def get_linesize(self) -> int:
        return self._font.get_linesize()

    def metrics(self, text: str):
        return self._font.metrics(text)


def set_lang(lang: str):
    """切换语言，清空缓存以便下次 get_font 加载对应字体"""
    global _current_lang
    if lang != _current_lang:
        _current_lang = lang
        _font_cache.clear()


def get_font(size: int) -> pygame.font.Font:
    # 中文像素字体最低 14px 保底；发布包使用 OFL 授权的 Fusion Pixel。
    actual = size
    if _current_lang == "zh":
        actual = max(14, size)
    key = (_current_lang, actual)
    if key not in _font_cache:
        if _current_lang == "zh":
            raw = pygame.font.Font(FONT_ZH, actual)
            _font_cache[key] = _BoldFontWrapper(raw)
        else:
            _font_cache[key] = pygame.font.Font(FONT_EN, actual)
    return _font_cache[key]
