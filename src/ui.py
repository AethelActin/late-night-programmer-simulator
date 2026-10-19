import pygame
import random
from src.config import (
    PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT,
    VIBE_HIGH_THRESHOLD, VIBE_LOW_THRESHOLD,
)
from src.font_manager import get_font
from src.lang import (VIBE_LABEL, REALITY_LABEL, COMPILING,
                      CATEGORY as CAT_LANG, CAT_CAT, START_BTN, QUIT_BTN,
                      TITLE, LANG_TOGGLE, HOW_TO_PLAY_BTN, HOW_TO_PLAY_LABEL, HOW_TO_PLAY_TEXT,
                      MUSIC_TOGGLE, MUSIC_TOGGLE_MUTED,
                      EVENT_TITLE, EVENT_TEXT, CHOICE_TEXT,
                      SESSION_LABEL, SESSION_SHORT, SESSION_NORMAL, SESSION_LONG,
                      TAGLINES,
                      EXIT_BTN, EXIT_CONFIRM, EXIT_CONFIRM_BTN, EXIT_CANCEL_BTN)

# 当前语言（由 main.py 设置，默认 en）
_lang = "en"

def set_lang(lang: str):
    global _lang
    _lang = lang
    # 语言切换时刷新开始界面展示语
    _pick_taglines()


def _pick_taglines():
    pool = TAGLINES.get(_lang, TAGLINES["en"])
    count = random.randint(1, 2)
    draw_start_screen._taglines = random.sample(pool, count)

def _t(d: dict) -> str:
    return d.get(_lang, d.get("en", ""))


def _draw_bar(screen, x, y, w, h, ratio, color):
    """绘制细进度条"""
    fill_w = int(w * max(0, min(1, ratio)))
    pygame.draw.rect(screen, (30, 34, 40), (x, y, w, h))
    if fill_w > 0:
        pygame.draw.rect(screen, color, (x, y, fill_w, h))


def _bar_color(vibe: int):
    if vibe >= VIBE_HIGH_THRESHOLD:
        return (220, 160, 80)
    elif vibe <= VIBE_LOW_THRESHOLD:
        return (100, 110, 130)
    return (180, 160, 130)


def _jitter_offset(vibe: int) -> tuple:
    """低 vibe 时数字轻微抖动"""
    if vibe < VIBE_LOW_THRESHOLD:
        return (random.randint(-1, 1), random.randint(-1, 1))
    return (0, 0)


def draw_status_panel(screen: pygame.Surface, stats: dict, dt: float, is_done: bool = False):
    """绘制右上角状态面板（低对比度、细边框、小字体）"""
    x, y = PANEL_X, PANEL_Y
    w, h = PANEL_WIDTH, PANEL_HEIGHT

    # 半透明背景
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((10, 12, 16, 180))
    screen.blit(panel, (x, y))
    # 1px 细灰边框
    pygame.draw.rect(screen, (60, 64, 70), (x, y, w, h), 1)

    vibe = stats.get("vibe", 50)
    reality = stats.get("reality", 80)
    progress = stats.get("progress", 0)
    font_small = get_font(8)
    font_bar = get_font(7)

    jx, jy = _jitter_offset(vibe)

    # vibe 条
    label_vibe = font_small.render(_t(VIBE_LABEL), True, (160, 164, 170))
    screen.blit(label_vibe, (x + 8, y + 8))
    bc = _bar_color(vibe)
    _draw_bar(screen, x + 68, y + 10, w - 88, 8, vibe / 100, bc)
    value_vibe = font_bar.render(str(vibe), True, bc)
    screen.blit(value_vibe, (x + w - 20 + jx, y + 8 + jy))

    # sanity 条
    label_reality = font_small.render(_t(REALITY_LABEL), True, (160, 164, 170))
    screen.blit(label_reality, (x + 8, y + 28))
    _draw_bar(screen, x + 68, y + 30, w - 88, 8, reality / 100, (100, 130, 160))
    value_reality = font_bar.render(str(int(reality)), True, (140, 160, 180))
    screen.blit(value_reality, (x + w - 20 + jx, y + 28 + jy))

    # project progress 文字 + 点号循环
    if is_done and progress >= 100:
        done_text = "project completed" if _lang == "en" else "项目已完成"
        label_compile = font_bar.render(done_text, True, (100, 140, 100))
    else:
        dots = "." * ((int(stats.get("_compile_dots", 0)) % 3) + 1)
        stats["_compile_dots"] = stats.get("_compile_dots", 0) + dt * 2
        compile_label = _t(COMPILING)
        # 不稳定状态持续一段固定时间再切换
        if "_unstable_timer" not in stats:
            stats["_unstable_timer"] = 0.0
            stats["_unstable"] = False
        stats["_unstable_timer"] -= dt
        if stats["_unstable_timer"] <= 0:
            unstable_chance = max(0.05, 0.15 - progress / 100 * 0.12)
            stats["_unstable"] = random.random() < unstable_chance
            stats["_unstable_timer"] = random.uniform(3.0, 8.0)
        if stats["_unstable"]:
            status_text = "project status: unstable" if _lang == "en" else "项目状态：不稳定"
            compile_text = f"{status_text}{dots}"
        else:
            compile_text = f"{compile_label}: {int(progress)}%{dots}"
        label_compile = font_bar.render(compile_text, True, (80, 90, 100))
    screen.blit(label_compile, (x + 8 + jx, y + h - 16 + jy))


def apply_vibe_tint(screen: pygame.Surface, vibe: int):
    """根据 Vibe 值调整画面色调，高 vibe 暖黄，低 vibe 冷灰"""
    s = screen.get_size()
    if vibe >= VIBE_HIGH_THRESHOLD:
        overlay = pygame.Surface(s, pygame.SRCALPHA)
        overlay.fill((50, 30, 10, 25))
        screen.blit(overlay, (0, 0))
    elif vibe <= VIBE_LOW_THRESHOLD:
        overlay = pygame.Surface(s, pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 15))
        screen.blit(overlay, (0, 0))


def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """自动换行：按 \n 分段，再按 max_width 切分长行"""
    lines = []
    for paragraph in text.split("\n"):
        if font.size(paragraph)[0] <= max_width:
            lines.append(paragraph)
        else:
            # 简单字符级换行
            current = ""
            for char in paragraph:
                test = current + char
                if font.size(test)[0] > max_width:
                    lines.append(current)
                    current = char
                else:
                    current = test
            if current:
                lines.append(current)
    return lines


def draw_event_dialog(screen: pygame.Surface, event: dict, mouse_pos: tuple, alpha: int = 255):
    """
    绘制右上角事件弹窗（左对齐、终端风格）。
    alpha 用于淡出效果（255=不透明, 0=全透明）。
    返回按钮 rect 列表，供主循环检测点击。
    """
    sw, sh = screen.get_size()
    w, h = min(360, sw - 40), min(280, sh - 40)
    x = sw - w - 10
    y = 8

    # 在临时 canvas 上画所有内容
    canvas = pygame.Surface((w, h), pygame.SRCALPHA)

    # 背景
    canvas.fill((8, 10, 14, 210))
    pygame.draw.rect(canvas, (60, 64, 70), (0, 0, w, h), 1)

    # header 标签
    header = _t(CAT_LANG.get(event.get("type", ""), CAT_LANG.get("cozy")))
    if "cat" in event.get("id", ""):
        header = _t(CAT_CAT)

    font_small = get_font(10)
    header_surf = font_small.render(header, True, (100, 120, 140))
    canvas.blit(header_surf, (16, 12))

    # 标题
    event_id = event.get("id", "")
    title_text = _t(EVENT_TITLE.get(event_id, {}))
    if not title_text:
        title_text = event.get("title", "")
    font_title = get_font(12)
    title_surf = font_title.render(title_text, True, (200, 204, 210))
    canvas.blit(title_surf, (16, 34))

    # 文本
    font_text = get_font(10)
    text = _t(EVENT_TEXT.get(event_id, {}))
    if not text:
        text = event.get("text", "")
    lines = _wrap_text(text, font_text, w - 32)
    line_h = 18
    choices = event.get("choices", [])
    text_bottom = h - (len(choices) * 30 + 16) if choices else h - 12
    for i, line in enumerate(lines[:max(0, (text_bottom - 56) // line_h)]):
        line_surf = font_text.render(line, True, (150, 154, 160))
        canvas.blit(line_surf, (16, 56 + i * line_h))

    # 选项按钮
    button_rects = []
    if choices:
        btn_y = h - len(choices) * 30 - 8
        choice_translations = CHOICE_TEXT.get(event_id, [])
        for i, choice in enumerate(choices):
            choice_text = choice['text']
            if i < len(choice_translations):
                choice_text = _t(choice_translations[i])
            btn_text = f"[ {choice_text} ]"
            btn_surf = font_text.render(btn_text, True, (180, 184, 190))
            btn_rect = btn_surf.get_rect(topleft=(16, btn_y + i * 30))
            click_rect = pygame.Rect(10, btn_y + i * 30 - 4, w - 20, 26)
            if click_rect.move(x, y).collidepoint(mouse_pos):
                btn_surf = font_text.render(btn_text, True, (220, 224, 230))
                pygame.draw.rect(canvas, (80, 84, 90), click_rect, 1)
            canvas.blit(btn_surf, btn_rect)
            button_rects.append(click_rect)

    # 整体 alpha 输出到屏幕
    canvas.set_alpha(alpha)
    screen.blit(canvas, (x, y))
    # 将按钮坐标转为屏幕坐标，供主循环点击检测
    return [r.move(x, y) for r in button_rects]


def draw_toast(screen: pygame.Surface, event: dict):
    """右下角 toast 通知（old terminal 风格，无 emoji）"""
    sw, sh = screen.get_size()
    font = get_font(8)
    title = event.get("title", "")
    text = event.get("text", "").split("\n")[0] if event.get("text") else ""

    lines = [f"[ {title} ]", f"  {text[:50]}"]
    tw = max(font.size(l)[0] for l in lines) + 24
    th = len(lines) * 16 + 16
    x = sw - tw - 16
    y = sh - th - 16

    panel = pygame.Surface((tw, th), pygame.SRCALPHA)
    panel.fill((8, 10, 14, 200))
    screen.blit(panel, (x, y))
    pygame.draw.rect(screen, (50, 54, 60), (x, y, tw, th), 1)

    for i, line in enumerate(lines):
        surf = font.render(line, True, (140, 144, 150))
        screen.blit(surf, (x + 12, y + 8 + i * 16))


def draw_cozy_hint(screen: pygame.Surface, text: str, alpha: int):
    """左下角简短氛围提示"""
    if alpha <= 0:
        return
    font = get_font(8)
    surf = font.render(text, True, (100, 120, 140))
    surf.set_alpha(max(0, min(255, alpha)))
    sh = screen.get_height()
    screen.blit(surf, (16, sh - 24))


def draw_ambient_log(screen: pygame.Surface, logs: list, vibe: int):
    """左侧状态日志流，终端风格，最新在最下面最亮"""
    font = get_font(8)
    recent = logs[-6:] if len(logs) > 6 else logs
    count = len(recent)
    if count == 0:
        return
    start_y = 140
    # 从最旧（顶部）到最新（底部）渲染
    vibe_dim = max(80, 120 - (100 - vibe) // 2)
    for i, entry in enumerate(recent):
        # i=0 最旧最淡, i=count-1 最新最亮
        t = i / max(count - 1, 1)
        alpha = int(40 + 200 * t)
        raw = EVENT_TEXT.get(entry.get('id'), entry.get("text", ""))
        if isinstance(raw, dict):
            raw = raw.get(_lang, raw.get("en", ""))
        if not isinstance(raw, str):
            raw = str(raw)
        text = raw.split('\n')[0][:55]
        # 左侧日志不能侵入右侧事件面板。
        while text and font.size(f"> {text}")[0] > 540:
            text = text[:-1]
        color = (
            min(255, vibe_dim + 30 + int(40 * t)),
            min(255, vibe_dim + 10 + int(30 * t)),
            max(60, vibe_dim - 20 + int(20 * t)),
        )
        surf = font.render(f"> {text}", True, color)
        surf.set_alpha(alpha)
        screen.blit(surf, (PANEL_X + 4, start_y + i * 16))


def draw_start_screen(screen: pygame.Surface, mouse_pos: tuple, music_muted: bool = False,
                      music_available: bool = True) -> tuple:
    """开始界面，返回 (button_rects, lang_btn_rect, music_btn_rect)"""
    sw, sh = screen.get_size()
    big = _lang == "zh"
    font_title = get_font(28 if big else 22)
    font_btn = get_font(20 if big else 16)

    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((10, 12, 16, 235))
    screen.blit(overlay, (0, 0))

    title_text = _t(TITLE)
    title = font_title.render(title_text, True, (180, 184, 190))
    tx = (sw - title.get_width()) // 2
    screen.blit(title, (tx, sh // 2 - 90))

    start_text = _t(START_BTN)
    start = font_btn.render(start_text, True, (180, 184, 190))
    sr = start.get_rect(center=(sw // 2, sh // 2))
    if sr.collidepoint(mouse_pos):
        start = font_btn.render(start_text, True, (220, 224, 230))
        pygame.draw.rect(screen, (80, 84, 90), sr.inflate(16, 8), 1)
    else:
        pygame.draw.rect(screen, (60, 64, 70), sr.inflate(16, 8), 1)
    screen.blit(start, sr)

    # 玩法按钮
    how_text = _t(HOW_TO_PLAY_BTN)
    how_surf = font_btn.render(how_text, True, (150, 154, 160))
    hr = how_surf.get_rect(center=(sw // 2, sh // 2 + 50))
    if hr.collidepoint(mouse_pos):
        how_surf = font_btn.render(how_text, True, (220, 224, 230))
        pygame.draw.rect(screen, (80, 84, 90), hr.inflate(16, 8), 1)
    else:
        pygame.draw.rect(screen, (60, 64, 70), hr.inflate(16, 8), 1)
    screen.blit(how_surf, hr)

    quit_text = _t(QUIT_BTN)
    quit_txt = font_btn.render(quit_text, True, (160, 120, 120))
    qr = quit_txt.get_rect(center=(sw // 2, sh // 2 + 100))
    if qr.collidepoint(mouse_pos):
        quit_txt = font_btn.render(quit_text, True, (200, 140, 140))
        pygame.draw.rect(screen, (80, 60, 60), qr.inflate(16, 8), 1)
    else:
        pygame.draw.rect(screen, (60, 50, 50), qr.inflate(16, 8), 1)
    screen.blit(quit_txt, qr)

    # 音乐开关（左下角）
    music_label = _t(MUSIC_TOGGLE_MUTED) if music_muted else _t(MUSIC_TOGGLE)
    if not music_available:
        music_label = 'music: unavailable' if _lang == 'en' else '本版无配乐'
    music_btn = font_btn.render(music_label, True, (120, 130, 150))
    mr = music_btn.get_rect(bottomleft=(16, sh - 16))
    if mr.collidepoint(mouse_pos):
        music_btn = font_btn.render(music_label, True, (180, 190, 210))
        pygame.draw.rect(screen, (70, 74, 80), mr.inflate(12, 6), 1)
    else:
        pygame.draw.rect(screen, (50, 54, 60), mr.inflate(12, 6), 1)
    screen.blit(music_btn, mr)

    lang_label = _t(LANG_TOGGLE)
    lang_btn = font_btn.render(lang_label, True, (120, 130, 150))
    lr = lang_btn.get_rect(bottomright=(sw - 16, sh - 16))
    if lr.collidepoint(mouse_pos):
        lang_btn = font_btn.render(lang_label, True, (180, 190, 210))
        pygame.draw.rect(screen, (70, 74, 80), lr.inflate(12, 6), 1)
    else:
        pygame.draw.rect(screen, (50, 54, 60), lr.inflate(12, 6), 1)
    screen.blit(lang_btn, lr)

    # 底部随机展示语
    if not hasattr(draw_start_screen, "_taglines"):
        _pick_taglines()
    for li, line in enumerate(draw_start_screen._taglines):
        surf = get_font(14).render(line, True, (100, 110, 125))
        screen.blit(surf, ((sw - surf.get_width()) // 2, sh - 80 + li * 16))

    return [sr, hr, qr], lr, mr


def draw_session_screen(screen: pygame.Surface, mouse_pos: tuple) -> tuple:
    """时长选择页面，返回 [short_rect, normal_rect, long_rect, back_rect]"""
    sw, sh = screen.get_size()
    big = _lang == "zh"
    font_title = get_font(28 if big else 22)
    font_btn = get_font(20 if big else 16)

    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((10, 12, 16, 235))
    screen.blit(overlay, (0, 0))

    label = _t(SESSION_LABEL)
    title = font_title.render(label, True, (180, 184, 190))
    tx = (sw - title.get_width()) // 2
    screen.blit(title, (tx, sh // 2 - 80))

    opts = [_t(SESSION_SHORT), _t(SESSION_NORMAL), _t(SESSION_LONG)]
    rects = []
    for i, opt in enumerate(opts):
        surf = font_btn.render(opt, True, (150, 154, 160))
        r = surf.get_rect(center=(sw // 2, sh // 2 - 10 + i * 50))
        click_r = r.inflate(24, 10)
        if click_r.collidepoint(mouse_pos):
            surf = font_btn.render(opt, True, (220, 224, 230))
            pygame.draw.rect(screen, (80, 84, 90), click_r, 1)
        screen.blit(surf, r)
        rects.append(click_r)

    # 返回按钮
    back_text = "[ back ]" if _lang == "en" else "[ 返回 ]"
    back = get_font(14 if big else 10).render(back_text, True, (140, 120, 120))
    br = back.get_rect(center=(sw // 2, sh // 2 + 130))
    if br.collidepoint(mouse_pos):
        back = get_font(14 if big else 10).render(back_text, True, (200, 160, 160))
        pygame.draw.rect(screen, (80, 60, 60), br.inflate(16, 8), 1)
    screen.blit(back, br)
    rects.append(br)

    return rects


def draw_how_to_play_screen(screen: pygame.Surface, mouse_pos: tuple) -> pygame.Rect:
    """玩法介绍页面，返回返回按钮 rect"""
    sw, sh = screen.get_size()
    big = _lang == "zh"
    font_title = get_font(20 if big else 16)
    font_text = get_font(14 if big else 10)

    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((10, 12, 16, 235))
    screen.blit(overlay, (0, 0))

    label = _t(HOW_TO_PLAY_LABEL)
    title = font_title.render(label, True, (180, 184, 190))
    screen.blit(title, ((sw - title.get_width()) // 2, 40))

    lines = _t(HOW_TO_PLAY_TEXT)
    line_h = 28 if big else 20
    start_y = (sh - len(lines) * line_h) // 2
    for i, line in enumerate(lines):
        if not line:
            continue
        surf = font_text.render(line, True, (150, 154, 160))
        screen.blit(surf, ((sw - surf.get_width()) // 2, start_y + i * line_h))

    # 返回按钮
    back_text = "[ back ]" if _lang == "en" else "[ 返回 ]"
    back = get_font(14 if big else 10).render(back_text, True, (140, 120, 120))
    br = back.get_rect(center=(sw // 2, sh - 40))
    if br.collidepoint(mouse_pos):
        back = get_font(14 if big else 10).render(back_text, True, (200, 160, 160))
        pygame.draw.rect(screen, (80, 60, 60), br.inflate(16, 8), 1)
    screen.blit(back, br)

    return br


def draw_exit_button(screen: pygame.Surface, mouse_pos: tuple) -> pygame.Rect:
    """左下角绘制 exit 按钮，返回点击区域 rect"""
    font = get_font(10)
    text = _t(EXIT_BTN)
    surf = font.render(text, True, (150, 120, 120))
    sw, sh = screen.get_size()
    btn_rect = surf.get_rect(bottomleft=(16, sh - 16))
    click_rect = btn_rect.inflate(12, 6)
    if click_rect.collidepoint(mouse_pos):
        surf = font.render(text, True, (200, 140, 140))
        pygame.draw.rect(screen, (80, 60, 60), click_rect, 1)
    else:
        pygame.draw.rect(screen, (60, 50, 50), click_rect, 1)
    screen.blit(surf, btn_rect)
    return click_rect


def draw_exit_confirm_dialog(screen: pygame.Surface, mouse_pos: tuple) -> tuple:
    """全屏半透明遮盖 + 居中确认弹窗，返回 (confirm_rect, cancel_rect)"""
    sw, sh = screen.get_size()
    font = get_font(12)
    font_btn = get_font(10)

    # 全屏半透明遮盖
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    # 弹窗尺寸
    dw, dh = 240, 100
    dx = (sw - dw) // 2
    dy = (sh - dh) // 2

    # 弹窗背景
    panel = pygame.Surface((dw, dh), pygame.SRCALPHA)
    panel.fill((10, 12, 16, 230))
    screen.blit(panel, (dx, dy))
    pygame.draw.rect(screen, (60, 64, 70), (dx, dy, dw, dh), 1)

    # 确认文字
    text = _t(EXIT_CONFIRM)
    surf = font.render(text, True, (180, 184, 190))
    tx = dx + (dw - surf.get_width()) // 2
    screen.blit(surf, (tx, dy + 24))

    # 确认按钮
    confirm_text = _t(EXIT_CONFIRM_BTN)
    confirm_surf = font_btn.render(confirm_text, True, (150, 180, 150))
    cr = confirm_surf.get_rect(center=(dx + dw // 2 - 60, dy + dh - 28))
    click_cr = cr.inflate(12, 6)
    if click_cr.collidepoint(mouse_pos):
        confirm_surf = font_btn.render(confirm_text, True, (180, 220, 180))
        pygame.draw.rect(screen, (60, 80, 60), click_cr, 1)
    else:
        pygame.draw.rect(screen, (50, 64, 50), click_cr, 1)
    screen.blit(confirm_surf, cr)

    # 取消按钮
    cancel_text = _t(EXIT_CANCEL_BTN)
    cancel_surf = font_btn.render(cancel_text, True, (150, 120, 120))
    cancel_r = cancel_surf.get_rect(center=(dx + dw // 2 + 60, dy + dh - 28))
    click_cancel_r = cancel_r.inflate(12, 6)
    if click_cancel_r.collidepoint(mouse_pos):
        cancel_surf = font_btn.render(cancel_text, True, (200, 140, 140))
        pygame.draw.rect(screen, (80, 60, 60), click_cancel_r, 1)
    else:
        pygame.draw.rect(screen, (60, 50, 50), click_cancel_r, 1)
    screen.blit(cancel_surf, cancel_r)

    return (click_cr, click_cancel_r)
