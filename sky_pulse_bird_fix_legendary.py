
"""
Sky Pulse Bird

Cleaned version tuned for pygame-ce, numpy, and Python 3.14.4.
"""

from __future__ import annotations

import json
import math
import random
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pygame

WIDTH, HEIGHT = 960, 540
FPS = 60
SAVE_FILE = Path(__file__).with_name("sky_pulse_bird_legendary_save.json")
GAME_TITLE = "Sky Pulse Bird"

WHITE = (245, 245, 245)
BLACK = (15, 18, 26)

def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3

def rgb_lerp(a: Tuple[int, int, int], b: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))

def ease_out_quart(t: float) -> float:
    return 1 - (1 - t) ** 4

def today_key(d: Optional[date] = None) -> str:
    d = d or date.today()
    return d.strftime("%Y-%m-%d")

def week_key(d: Optional[date] = None) -> str:
    d = d or date.today()
    iso_year, iso_week, _ = d.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"

QUEST_TEMPLATES = {
    "daily": [
        {"key": "pipes", "title": "Pipe Sweep", "desc": "Score {target} pipes.", "stat": "pipes_scored", "target": (8, 14), "reward": (45, 70), "icon": "pipe"},
        {"key": "coins", "title": "Coin Pulse", "desc": "Collect {target} coins.", "stat": "coins_collected", "target": (80, 160), "reward": (45, 80), "icon": "coin"},
        {"key": "flaps", "title": "Sky Rhythm", "desc": "Flap {target} times.", "stat": "flaps", "target": (35, 65), "reward": (40, 75), "icon": "wing"},
        {"key": "items", "title": "Supply Run", "desc": "Collect {target} items.", "stat": "items_total", "target": (6, 12), "reward": (50, 85), "icon": "crate"},
        {"key": "time", "title": "Long Glide", "desc": "Play for {target} seconds.", "stat": "play_time", "target": (90, 150), "reward": (45, 80), "icon": "clock"},
        {"key": "boosts", "title": "Boost Charge", "desc": "Collect {target} boost items.", "stat": "item:boost", "target": (2, 5), "reward": (50, 85), "icon": "bolt"},
        {"key": "shields", "title": "Shield Drill", "desc": "Block {target} hits with a shield.", "stat": "shield_breaks", "target": (2, 4), "reward": (55, 90), "icon": "shield"},
    ],
    "weekly": [
        {"key": "boss_wins", "title": "Boss Breaker", "desc": "Defeat {target} bosses.", "stat": "boss_wins", "target": (1, 3), "reward": (140, 220), "icon": "boss"},
        {"key": "boss_damage", "title": "Core Pressure", "desc": "Deal {target} boss damage.", "stat": "boss_damage_dealt", "target": (6, 14), "reward": (130, 210), "icon": "core"},
        {"key": "runs", "title": "Road Worker", "desc": "Finish {target} runs.", "stat": "runs", "target": (4, 8), "reward": (120, 190), "icon": "run"},
        {"key": "wins", "title": "Clean Flight", "desc": "Win {target} runs.", "stat": "wins", "target": (2, 4), "reward": (150, 230), "icon": "trophy"},
        {"key": "legend", "title": "Legend Lane", "desc": "Score {target} pipes total.", "stat": "pipes_scored", "target": (45, 80), "reward": (150, 240), "icon": "star"},
        {"key": "rare", "title": "Rare Supply", "desc": "Collect {target} rare items.", "stat": "item:multiplier", "target": (2, 5), "reward": (140, 220), "icon": "gem"},
        {"key": "time", "title": "Endurance Run", "desc": "Play for {target} seconds.", "stat": "play_time", "target": (420, 720), "reward": (150, 240), "icon": "clock"},
    ],
}

ACHIEVEMENT_SPECS = [
    {"key": "first_flap", "name": "First Flight", "desc": "Flap once.", "stat": "flaps", "target": 1, "icon": "wing"},
    {"key": "airborne", "name": "Airborne", "desc": "Play for 90 seconds.", "stat": "play_time", "target": 90, "icon": "clock"},
    {"key": "pipe_ace", "name": "Pipe Ace", "desc": "Score 25 pipes.", "stat": "pipes_scored", "target": 25, "icon": "pipe"},
    {"key": "coin_hoard", "name": "Coin Hoard", "desc": "Collect 250 coins.", "stat": "coins_collected", "target": 250, "icon": "coin"},
    {"key": "item_lover", "name": "Item Lover", "desc": "Collect 40 items.", "stat": "items_total", "target": 40, "icon": "crate"},
    {"key": "shield_guard", "name": "Shield Guard", "desc": "Block 4 hits with shields.", "stat": "shield_breaks", "target": 4, "icon": "shield"},
    {"key": "boss_breaker", "name": "Boss Breaker", "desc": "Defeat one boss.", "stat": "boss_wins", "target": 1, "icon": "boss"},
    {"key": "boss_master", "name": "Boss Master", "desc": "Defeat 4 bosses.", "stat": "boss_wins", "target": 4, "icon": "crown"},
    {"key": "hard_fighter", "name": "Hard Fighter", "desc": "Defeat a boss on Hard.", "stat": "boss_wins_hard", "target": 1, "icon": "medal"},
    {"key": "daily_runner", "name": "Daily Runner", "desc": "Complete 3 daily quests.", "stat": "daily_complete", "target": 3, "icon": "quest"},
    {"key": "weekly_champ", "name": "Weekly Champ", "desc": "Complete 3 weekly quests.", "stat": "weekly_complete", "target": 3, "icon": "star"},
    {"key": "veteran", "name": "Veteran", "desc": "Finish 20 runs.", "stat": "runs", "target": 20, "icon": "trophy"},
    {"key": "sky_runner", "name": "Sky Runner", "desc": "Finish 5 runs.", "stat": "runs", "target": 5, "icon": "run"},
    {"key": "pipe_veteran", "name": "Pipe Veteran", "desc": "Score 100 pipes.", "stat": "pipes_scored", "target": 100, "icon": "pipe"},
    {"key": "coin_collector", "name": "Coin Collector", "desc": "Collect 1000 coins.", "stat": "coins_collected", "target": 1000, "icon": "coin"},
    {"key": "combo_spark", "name": "Combo Spark", "desc": "Reach a combo of 10.", "stat": "best_combo", "target": 10, "icon": "star"},
    {"key": "marathon", "name": "Marathon", "desc": "Play for 600 seconds.", "stat": "play_time", "target": 600, "icon": "clock"},
    {"key": "boss_hunter", "name": "Boss Hunter", "desc": "Defeat 10 bosses.", "stat": "boss_wins", "target": 10, "icon": "boss"},
    {"key": "hard_conqueror", "name": "Hard Conqueror", "desc": "Defeat 3 bosses on Hard.", "stat": "boss_wins_hard", "target": 3, "icon": "medal"},
    {"key": "quest_legend", "name": "Quest Legend", "desc": "Complete 10 daily quests.", "stat": "daily_complete", "target": 10, "icon": "quest"},
]
LEGACY_SKIN_ORDER = [
    "CLASSIC", "NEON", "EMBER", "AQUA", "SHADOW", "ROYAL", "CHERRY", "CRYSTAL",
    "SOLAR", "VIOLET", "MINT", "VOID", "GHOST", "PIXEL", "LAGOON", "LAVA",
    "AURORA", "PRISM", "CYBER", "FROST", "GALAXY", "SAND", "ROSE", "STEEL", "CORAL",
]

def sentence_case(text: str) -> str:
    text = (text or "").strip()
    return text[:1].upper() + text[1:] if text else text

def skin_name_from_legacy_index(idx: int) -> str:
    if 0 <= idx < len(LEGACY_SKIN_ORDER):
        return LEGACY_SKIN_ORDER[idx]
    return LEGACY_SKIN_ORDER[0]

def skin_index_from_name(name: str) -> int:
    name = str(name).upper()
    for i, skin in enumerate(SKINS):
        if skin.name.upper() == name:
            return i
    return 0

def skin_index_from_legacy_index(idx: int) -> int:
    return skin_index_from_name(skin_name_from_legacy_index(idx))

def build_gradient_surface(top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> pygame.Surface:
    arr = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    ys = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None]
    grad = np.array(top, dtype=np.float32) * (1 - ys) + np.array(bottom, dtype=np.float32) * ys
    arr[:] = grad[:, None, :].astype(np.uint8)
    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))



def get_cloud_surface(scale: float, color: Tuple[int, int, int]) -> pygame.Surface:
    scale = max(0.3, float(scale))
    w = max(18, int(90 * scale))
    h = max(10, int(42 * scale))
    key = (w, h, color)
    cloud = _CLOUD_CACHE.get(key)
    if cloud is None:
        cloud = pygame.Surface((w + 40, h + 20), pygame.SRCALPHA)
        c = (*color, 180)
        pygame.draw.ellipse(cloud, c, (8, 10, w * 0.5, h * 0.72))
        pygame.draw.ellipse(cloud, c, (w * 0.25, 4, w * 0.45, h * 0.95))
        pygame.draw.ellipse(cloud, c, (w * 0.53, 12, w * 0.40, h * 0.68))
        _CLOUD_CACHE[key] = cloud
    return cloud


def build_arcade_background_scene(theme: dict, theme_index: int) -> dict:
    base = build_gradient_surface(theme["sky_top"], theme["sky_bottom"]).convert()
    static = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    rng = random.Random(0xA11CE + theme_index * 1009)
    haze = theme["haze"]
    pipe = theme["pipe"]
    pipe_dark = theme["pipe_dark"]
    cloud = theme["cloud"]

    # Common cinematic glow.
    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*haze, 28), pygame.Rect(-120, -48, WIDTH + 240, 200))
    pygame.draw.ellipse(glow, (*pipe, 18), pygame.Rect(WIDTH // 2 - 320, -20, 640, 170))
    static.blit(glow, (0, 0))

    clouds = []
    sparkles = []
    ribbons = []

    def ridge(points, color):
        pygame.draw.polygon(static, color, points)

    def add_cloud(x, y, scale, speed, mix=0.0):
        c = rgb_lerp(cloud, haze, mix)
        surf = get_cloud_surface(scale, c)
        clouds.append((surf, float(x), float(y), float(speed), float(rng.uniform(-1.5, 1.5))))

    kind = theme["name"]

    if kind == "DAWN":
        # Warm dawn with layered hills and a reflective distance.
        sun_center = (WIDTH - 150, 94)
        sun_radius = 54
        pygame.draw.circle(static, (*cloud, 150), sun_center, sun_radius)
        pygame.draw.circle(static, (*haze, 110), sun_center, 92, 8)
        ridge([(0, 330), (92, 286), (168, 304), (258, 260), (356, 286), (454, 242), (562, 272), (682, 228), (790, 262), (WIDTH, 240), (WIDTH, HEIGHT), (0, HEIGHT)], (74, 102, 148))
        ridge([(0, 362), (126, 316), (214, 332), (306, 302), (402, 320), (504, 286), (614, 306), (726, 282), (850, 304), (WIDTH, 290), (WIDTH, HEIGHT), (0, HEIGHT)], (44, 72, 112))
        ridge([(0, 396), (148, 360), (248, 372), (362, 340), (478, 354), (586, 326), (702, 338), (816, 316), (WIDTH, 328), (WIDTH, HEIGHT), (0, HEIGHT)], (28, 44, 72))
        pygame.draw.rect(static, theme["ground"], (0, HEIGHT - 76, WIDTH, 76))
        pygame.draw.rect(static, pipe, (0, HEIGHT - 76, WIDTH, 8))
        for i in range(5):
            x = 80 + i * 156 + rng.randint(-12, 12)
            y = 78 + (i % 2) * 16
            pygame.draw.arc(static, (*haze, 58), (x - 56, y - 8, 124, 46), 0.18, 3.0, 3)
        for i in range(6):
            add_cloud(rng.randint(-50, WIDTH - 40), rng.randint(42, 150), rng.uniform(0.58, 1.18), rng.uniform(9.0, 18.0), rng.random() * 0.55)
        sparkles = [(rng.randint(0, WIDTH), rng.randint(10, 190), rng.randint(1, 2), rng.random(), cloud) for _ in range(10)]

    elif kind == "NIGHT":
        # Night skyline with stars and a subtle aurora ribbon.
        for i in range(70):
            x = rng.randint(0, WIDTH - 1)
            y = rng.randint(8, 200)
            r = 1 if i % 5 else 2
            pygame.draw.circle(static, (*cloud, 210 if r == 2 else 150), (x, y), r)
        pygame.draw.circle(static, (*cloud, 180), (WIDTH - 150, 86), 26)
        pygame.draw.circle(static, (*haze, 75), (WIDTH - 150, 86), 52, 2)
        ribbons = [
            [(0, 164), (120, 146), (246, 156), (378, 132), (498, 148), (628, 126), (756, 138), (WIDTH, 122)],
            [(0, 194), (130, 178), (244, 188), (372, 168), (508, 182), (646, 166), (780, 174), (WIDTH, 160)],
        ]
        for band, color in zip(ribbons, ((62, 122, 196), (30, 82, 132))):
            pygame.draw.lines(static, color, False, band, 12)
        skyline = [(0, 390), (58, 390), (58, 336), (92, 336), (92, 362), (118, 362), (118, 314), (148, 314),
                   (148, 350), (178, 350), (178, 302), (212, 302), (212, 372), (248, 372), (248, 330),
                   (282, 330), (282, 300), (322, 300), (322, 352), (356, 352), (356, 286), (392, 286),
                   (392, 362), (432, 362), (432, 320), (470, 320), (470, 294), (516, 294), (516, 344),
                   (552, 344), (552, 306), (594, 306), (594, 350), (632, 350), (632, 290), (676, 290),
                   (676, 372), (720, 372), (720, 324), (760, 324), (760, 296), (808, 296), (808, 352),
                   (850, 352), (850, 316), (896, 316), (896, 388), (WIDTH, 388), (WIDTH, HEIGHT), (0, HEIGHT)]
        ridge(skyline, (18, 26, 42))
        ridge([(0, 420), (180, 398), (354, 414), (520, 394), (724, 410), (WIDTH, 402), (WIDTH, HEIGHT), (0, HEIGHT)], (10, 14, 24))
        pygame.draw.rect(static, theme["ground"], (0, HEIGHT - 72, WIDTH, 72))
        pygame.draw.rect(static, pipe, (0, HEIGHT - 72, WIDTH, 8))
        for i in range(4):
            add_cloud(rng.randint(-60, WIDTH - 40), rng.randint(42, 130), rng.uniform(0.48, 0.92), rng.uniform(4.0, 9.0), rng.random() * 0.4 + 0.15)
        sparkles = [(rng.randint(0, WIDTH), rng.randint(20, 190), rng.randint(1, 2), rng.random(), cloud) for _ in range(24)]

    elif kind == "EMBER":
        # Volcanic ridges and a molten horizon.
        ridge([(0, 320), (100, 260), (196, 286), (280, 238), (376, 272), (472, 220), (584, 252), (676, 198), (794, 244), (WIDTH, 208), (WIDTH, HEIGHT), (0, HEIGHT)], (110, 46, 34))
        ridge([(0, 356), (132, 312), (220, 334), (326, 298), (430, 318), (532, 286), (646, 312), (750, 270), (880, 298), (WIDTH, 288), (WIDTH, HEIGHT), (0, HEIGHT)], (72, 26, 22))
        ridge([(0, 402), (152, 372), (266, 386), (374, 356), (490, 370), (604, 340), (716, 358), (824, 334), (WIDTH, 346), (WIDTH, HEIGHT), (0, HEIGHT)], (34, 18, 18))
        pygame.draw.rect(static, theme["ground"], (0, HEIGHT - 86, WIDTH, 86))
        pygame.draw.rect(static, pipe, (0, HEIGHT - 86, WIDTH, 10))
        for i in range(8):
            x = 52 + i * 122
            pygame.draw.line(static, (210, 70, 18), (x, HEIGHT - 86), (x + 18, HEIGHT - 28), 3)
            pygame.draw.line(static, (255, 148, 40), (x + 8, HEIGHT - 80), (x + 28, HEIGHT - 30), 1)
        for i in range(5):
            sx = 88 + i * 182
            pygame.draw.arc(static, (*haze, 90), (sx - 54, 26, 118, 72), 0.18, 2.95, 4)
            pygame.draw.arc(static, (*pipe_dark, 120), (sx - 42, 42, 96, 48), 0.24, 2.7, 2)
        for i in range(6):
            add_cloud(rng.randint(-50, WIDTH - 40), rng.randint(38, 136), rng.uniform(0.52, 1.0), rng.uniform(5.0, 10.0), rng.random() * 0.4 + 0.35)
        sparkles = [(rng.randint(0, WIDTH), rng.randint(20, 210), rng.randint(1, 2), rng.random(), haze if i % 2 else cloud) for i in range(30)]

    else:  # AURORA
        # Shimmering aurora curtains over layered mountains and reflective water.
        ribbons = [
            [(0, 82), (84, 62), (172, 88), (256, 58), (350, 82), (454, 44), (552, 76), (662, 52), (776, 84), (WIDTH, 54)],
            [(0, 118), (82, 102), (168, 124), (254, 100), (342, 118), (442, 88), (560, 114), (684, 96), (804, 122), (WIDTH, 88)],
            [(0, 150), (94, 138), (190, 152), (284, 130), (388, 150), (490, 122), (590, 146), (704, 126), (818, 154), (WIDTH, 136)],
        ]
        ribbon_colors = ((128, 255, 220), (82, 188, 255), (182, 140, 255))
        for band, color in zip(ribbons, ribbon_colors):
            pygame.draw.lines(static, color, False, band, 8)
        ridge([(0, 330), (82, 292), (188, 304), (274, 260), (384, 288), (494, 242), (608, 272), (718, 232), (842, 270), (WIDTH, 246), (WIDTH, HEIGHT), (0, HEIGHT)], (56, 92, 132))
        ridge([(0, 376), (130, 342), (228, 356), (332, 326), (442, 344), (560, 314), (682, 332), (790, 304), (WIDTH, 320), (WIDTH, HEIGHT), (0, HEIGHT)], (24, 58, 86))
        pygame.draw.rect(static, theme["ground"], (0, HEIGHT - 74, WIDTH, 74))
        pygame.draw.rect(static, pipe, (0, HEIGHT - 74, WIDTH, 8))
        # Reflections on the waterline.
        for i in range(7):
            x = 70 + i * 128
            pygame.draw.line(static, (*haze, 88), (x, HEIGHT - 118), (x + 48, HEIGHT - 84), 2)
            pygame.draw.line(static, (*cloud, 50), (x + 14, HEIGHT - 112), (x + 46, HEIGHT - 88), 1)
        for i in range(5):
            add_cloud(rng.randint(-50, WIDTH - 40), rng.randint(40, 132), rng.uniform(0.50, 1.02), rng.uniform(5.0, 10.0), rng.random() * 0.5)
        sparkles = [(rng.randint(0, WIDTH), rng.randint(10, 190), rng.randint(1, 2), rng.random(), cloud if i % 2 else haze) for i in range(20)]

    return {
        "base": base,
        "static": static.convert_alpha(),
        "clouds": clouds,
        "sparkles": sparkles,
        "ribbons": ribbons,
        "kind": kind,
        "haze": haze,
        "cloud": cloud,
        "pipe": pipe,
        "pipe_dark": pipe_dark,
        "sun": {"center": (WIDTH - 150, 94), "radius": 54},
    }
def draw_round_rect(surf: pygame.Surface, color, rect, radius: int = 18, width: int = 0):
    rect = pygame.Rect(rect)
    if width:
        pygame.draw.rect(surf, color, rect, width=width, border_radius=radius)
        return

    # Cache fully rendered panels so repeated buttons / UI cards stop rebuilding
    # the same rounded-rect artwork every frame.
    key = (rect.size, color, radius)
    panel = _ROUND_RECT_CACHE.get(key)
    if panel is None:
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, color, panel.get_rect(), border_radius=radius)

        # Soft top sheen.
        top_h = max(5, rect.height // 4)
        top = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            top,
            (255, 255, 255, 26),
            pygame.Rect(4, 4, rect.width - 8, top_h),
            border_radius=max(2, radius - 4),
        )
        pygame.draw.rect(
            top,
            (255, 255, 255, 18),
            pygame.Rect(6, 6, max(8, rect.width // 8), rect.height - 12),
            border_radius=max(2, radius - 6),
        )

        # Gentle bottom depth to make the box feel rounded and raised.
        bottom = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            bottom,
            (0, 0, 0, 28),
            pygame.Rect(4, rect.height - top_h - 2, rect.width - 8, top_h + 2),
            border_radius=max(2, radius - 4),
        )

        # Diagonal glossy sweep, very subtle so it does not hurt readability.
        sweep = pygame.Surface((rect.width * 2, rect.height * 2), pygame.SRCALPHA)
        sx = sweep.get_width() // 2
        for dx in range(-max(6, rect.width // 7), max(6, rect.width // 7) + 1):
            dist = abs(dx) / float(max(1, rect.width // 7))
            if dist > 1:
                continue
            alpha = int(70 * (1 - dist) ** 1.7)
            pygame.draw.line(
                sweep,
                (255, 255, 255, alpha),
                (sx + dx - rect.width // 2, 0),
                (sx + dx - rect.width, sweep.get_height()),
                1,
            )
        sweep = pygame.transform.rotate(sweep, -18)

        # Clip everything to the rounded rectangle.
        clip = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(clip, (255, 255, 255, 255), clip.get_rect(), border_radius=radius)
        panel.blit(top, (0, 0))
        panel.blit(bottom, (0, 0))
        panel.blit(sweep, (-sweep.get_width() // 2 + rect.width // 6, -sweep.get_height() // 2))
        panel.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _ROUND_RECT_CACHE[key] = panel
        _trim_cache(_ROUND_RECT_CACHE, 512)

    surf.blit(panel, rect.topleft)

def draw_round_outline(surf: pygame.Surface, color, rect, radius: int = 18, width: int = 2):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surf, color, rect, width=width, border_radius=radius)

def draw_round_flash(surf: pygame.Surface, rect: pygame.Rect, radius: int, alpha: int):
    flash = get_clear_surface(rect.size, ("round_flash", rect.size))
    tick = pygame.time.get_ticks() * 0.0048
    pulse = 0.72 + 0.28 * math.sin(tick + rect.x * 0.018 + rect.y * 0.022 + rect.width * 0.004)
    alpha = int(clamp(alpha * pulse, 0, 255))
    if alpha <= 0:
        return
    pygame.draw.rect(flash, (255, 255, 255, alpha), flash.get_rect(), border_radius=radius)

    sheen = get_clear_surface(rect.size, ("round_sheen", rect.size))
    top_h = max(5, rect.height // 3)
    sheen_alpha = int(clamp(alpha * 0.42, 0, 255))
    pygame.draw.rect(
        sheen,
        (255, 255, 255, sheen_alpha),
        (4, 4, rect.width - 8, top_h),
        border_radius=max(1, radius - 4),
    )
    flash.blit(sheen, (0, 0))
    surf.blit(flash, rect.topleft)

def draw_text(surf, font, text, pos, color=WHITE, center=False, shadow=True, align: str = "left"):
    img = render_text_cached(font, text, color)
    rect = img.get_rect()
    align = ("center" if center else align or "left").lower()
    if align == "center":
        rect.center = pos
    elif align == "right":
        rect.topright = pos
    else:
        rect.topleft = pos
    if shadow:
        shadow_img = render_text_cached(font, text, (0, 0, 0))
        shadow_rect = shadow_img.get_rect()
        if align == "center":
            shadow_rect.center = (rect.centerx + 2, rect.centery + 2)
        elif align == "right":
            shadow_rect.topright = (rect.right + 2, rect.top + 2)
        else:
            shadow_rect.topleft = (rect.x + 2, rect.y + 2)
        surf.blit(shadow_img, shadow_rect)
    surf.blit(img, rect)
    return rect

_SYSFONT_CACHE = {}
_ROUND_RECT_CACHE = {}
_TEXT_CACHE = {}
_PARTICLE_CACHE = {}
_CLOUD_CACHE = {}
_PIPE_GAP_RING_CACHE = {}
_WORK_SURFACE_CACHE = {}
_BIRD_BODY_CACHE = {}
_ORB_BODY_CACHE = {}
ORB_PHASE_BUCKETS = 12
ORB_ARMS_4 = tuple((math.tau * i) / 4.0 for i in range(4))
ORB_ARMS_5 = tuple((math.tau * i) / 5.0 for i in range(5))
ORB_ARMS_6 = tuple((math.tau * i) / 6.0 for i in range(6))
ORB_ARMS_8 = tuple((math.tau * i) / 8.0 for i in range(8))
ORB_ARMS_16 = tuple((math.tau * i) / 16.0 for i in range(16))
BIRD_SHIELD_ARMS = tuple((math.tau * i) / 8.0 for i in range(8))


def _trim_cache(cache: dict, limit: int):
    while len(cache) > limit:
        try:
            cache.pop(next(iter(cache)))
        except StopIteration:
            break


def fast_rotate_surface(surface: pygame.Surface, angle: float) -> pygame.Surface:
    """Rotate only when necessary; avoids the extra scaling work of rotozoom."""
    angle = float(angle)
    if -1e-9 < angle < 1e-9:
        return surface
    return pygame.transform.rotate(surface, angle)


def retain_positive_life(items):
    """Compact an in-memory list of objects that expose a positive `life` field."""
    write = 0
    for item in items:
        if item.life > 0:
            items[write] = item
            write += 1
    del items[write:]


def retain_active_orbs(items):
    """Compact orbit/item lists while preserving their current order."""
    write = 0
    for item in items:
        if item.active and item.x > -80:
            items[write] = item
            write += 1
    del items[write:]


def retain_projectiles(items):
    """Compact projectile lists using the same culling window as the original code."""
    write = 0
    for item in items:
        if -80 < item.x < WIDTH + 80 and -80 < item.y < HEIGHT + 80:
            items[write] = item
            write += 1
    del items[write:]


def retain_clouds(items):
    """Compact cloud lists without allocating a fresh list every frame."""
    write = 0
    for item in items:
        if item.x > -180:
            items[write] = item
            write += 1
    del items[write:]

def get_pipe_gap_ring_surface(
    size: tuple[int, int],
    phase: int,
    accent: Tuple[int, int, int],
    core: Tuple[int, int, int],
    alpha: Optional[int] = None,
) -> pygame.Surface:
    """Return a reusable boss-gap ring overlay.

    The artwork is cached once per size/phase/tint pair. When an alpha is
    provided we cache that opacity bucket directly as well, which avoids
    allocating a fresh copy every frame in boss fights.
    """
    width = max(1, int(size[0]))
    height = max(1, int(size[1]))
    phase = max(1, int(phase))
    alpha_bucket = None if alpha is None else max(0, min(255, int(alpha)) // 8 * 8)
    key = (width, height, phase, accent, core, alpha_bucket)
    surf = _PIPE_GAP_RING_CACHE.get(key)
    if surf is None:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (*accent, 255), (12, 12, width - 24, height - 24), 4)
        pygame.draw.ellipse(surf, (*core, 255), (22, 22, width - 44, height - 44), 2)
        for i in range(phase):
            yy = 18 + i * max(10, height // max(2, phase + 1))
            pygame.draw.line(surf, (*core, 225), (16, yy), (width - 16, yy), 1)
        if phase >= 2:
            for i in range(3):
                ang = i * (math.tau / 3)
                x1 = width * 0.5 + int(math.cos(ang) * 14)
                y1 = height * 0.5 + int(math.sin(ang) * 8)
                x2 = width * 0.5 + int(math.cos(ang) * (width * 0.42))
                y2 = height * 0.5 + int(math.sin(ang) * (height * 0.34))
                pygame.draw.line(surf, (*accent, 180), (x1, y1), (x2, y2), 1)
        if phase >= 3:
            for i in range(6):
                x0 = 12 + i * (width - 24) // 6
                pygame.draw.circle(surf, (*core, 200), (x0, 14 + (i % 2) * (height - 28)), 2)
        if alpha_bucket is not None:
            surf.set_alpha(alpha_bucket)
        _PIPE_GAP_RING_CACHE[key] = surf
        _trim_cache(_PIPE_GAP_RING_CACHE, 384)
    return surf

def get_cached_sysfont(name: str, size: int, bold: bool = False, italic: bool = False):
    key = (name, size, bold, italic)
    font = _SYSFONT_CACHE.get(key)
    if font is None:
        font = pygame.font.SysFont(name, size, bold=bold, italic=italic)
        _SYSFONT_CACHE[key] = font
    return font


def render_text_cached(font, text: str, color: Tuple[int, int, int]):
    key = (id(font), str(text), tuple(color))
    img = _TEXT_CACHE.get(key)
    if img is None:
        img = font.render(str(text), True, color)
        _TEXT_CACHE[key] = img
        _trim_cache(_TEXT_CACHE, 1600)
    return img


def get_particle_surface(radius: int, color: Tuple[int, int, int], alpha: int):
    radius = max(1, int(radius))
    alpha = max(0, min(255, int(alpha)))
    bucket = (alpha // 8) * 8
    key = (radius, color, bucket)
    surf = _PARTICLE_CACHE.get(key)
    if surf is None:
        size = radius * 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, bucket), (radius * 2, radius * 2), radius)
        _PARTICLE_CACHE[key] = surf
        _trim_cache(_PARTICLE_CACHE, 4096)
    return surf



def get_clear_surface(size: tuple[int, int], key):
    """Return a reusable transparent surface cleared for immediate drawing."""
    size = (int(size[0]), int(size[1]))
    cache_key = (size, key)
    surf = _WORK_SURFACE_CACHE.get(cache_key)
    if surf is None or surf.get_size() != size:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        _WORK_SURFACE_CACHE[cache_key] = surf
        _trim_cache(_WORK_SURFACE_CACHE, 96)
    else:
        surf.fill((0, 0, 0, 0))
    return surf


def get_bird_body_surface(skin: Skin, radius: int) -> pygame.Surface:
    """Return the static (non-wing) bird sprite for a skin/radius pair."""
    radius = max(1, int(radius))
    key = (skin.name, radius)
    surf = _BIRD_BODY_CACHE.get(key)
    if surf is None:
        size = radius * 4
        surf = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        cx = cy = radius * 2
        r = radius
        body_col = skin.bird_main
        alt_col = skin.bird_alt
        beak = skin.bird_beak
        style = skin.fx

        pygame.draw.ellipse(surf, body_col, (cx - r, cy - int(r * 0.84), int(r * 1.95), int(r * 1.52)))
        pygame.draw.ellipse(surf, alt_col, (cx - int(r * 0.10), cy - int(r * 0.54), int(r * 1.02), int(r * 0.88)))
        pygame.draw.circle(surf, (255, 255, 255), (cx + 3, cy - 4), 5)
        pygame.draw.circle(surf, (20, 20, 25), (cx + 4, cy - 4), 2)
        pygame.draw.polygon(surf, beak, [(cx + 7, cy - 1), (cx + 19, cy + 3), (cx + 7, cy + 7)])

        if style == "NEON":
            pygame.draw.circle(surf, (*skin.accent, 65), (cx, cy), int(r * 1.55), 2)
            pygame.draw.line(surf, (*skin.accent, 120), (cx - 14, cy - 4), (cx - 28, cy - 10), 2)
        elif style == "EMBER":
            for i in range(4):
                fx = cx - 18 - i * 5
                fy = cy + 8 + i
                pygame.draw.polygon(surf, (255, 160 + i * 15, 60, 170), [(fx, fy), (fx - 8, fy + 2), (fx - 2, fy - 8)])
        elif style == "AQUA":
            for i in range(3):
                pygame.draw.circle(surf, (220, 255, 255, 110), (cx - 20 - i * 5, cy + 8 + i * 2), 2)
        elif style == "SHADOW" or style == "VOID":
            pygame.draw.circle(surf, (40, 44, 60, 110), (cx + 1, cy + 2), int(r * 1.35), 2)
            pygame.draw.line(surf, (220, 220, 255, 100), (cx - 8, cy + 14), (cx - 24, cy + 18), 1)
        elif style == "ROYAL":
            pygame.draw.polygon(surf, (255, 230, 120, 200), [(cx - 1, cy - 20), (cx + 5, cy - 28), (cx + 12, cy - 20), (cx + 18, cy - 27), (cx + 24, cy - 16), (cx - 1, cy - 16)])
        elif style == "CHERRY":
            pygame.draw.circle(surf, (255, 170, 195, 150), (cx - 18, cy + 10), 3)
            pygame.draw.circle(surf, (255, 170, 195, 150), (cx - 24, cy + 2), 2)
        elif style == "CRYSTAL":
            pygame.draw.line(surf, (255, 255, 255, 160), (cx - 14, cy - 14), (cx + 6, cy + 8), 2)
            pygame.draw.line(surf, (180, 250, 255, 160), (cx - 5, cy - 20), (cx + 16, cy - 2), 1)
        elif style == "SOLAR":
            for a in range(5):
                pygame.draw.line(surf, (255, 220, 100, 120), (cx - 4, cy - 16), (cx - 14 - a * 2, cy - 28 - a), 1)
        elif style == "VIOLET":
            pygame.draw.circle(surf, (255, 255, 255, 110), (cx - 18, cy - 10), 2)
            pygame.draw.circle(surf, (255, 180, 240, 110), (cx - 26, cy + 2), 1)
        elif style == "MINT":
            pygame.draw.arc(surf, (120, 255, 180, 130), (cx - 34, cy - 8, 24, 18), 0.2, 2.8, 2)
        elif style == "GHOST":
            pygame.draw.ellipse(surf, (240, 250, 255, 80), (cx - r + 2, cy - int(r * 0.62), int(r * 1.82), int(r * 1.32)))
        elif style == "PIXEL":
            pygame.draw.rect(surf, (255, 255, 255, 140), (cx - 21, cy - 18, 4, 4))
            pygame.draw.rect(surf, (90, 255, 190, 140), (cx - 26, cy - 4, 4, 4))

        _BIRD_BODY_CACHE[key] = surf
        _trim_cache(_BIRD_BODY_CACHE, 128)
    return surf


def get_orb_body_surface(kind: str, color: Tuple[int, int, int], phase_bucket: int, size: int = 88) -> pygame.Surface:
    """Return a cached orb sprite body before the final rotation."""
    size = max(24, int(size))
    phase_bucket = int(phase_bucket) % ORB_PHASE_BUCKETS
    key = (kind, tuple(color), phase_bucket, size)
    surf = _ORB_BODY_CACHE.get(key)
    if surf is not None:
        return surf

    surf = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
    cx = cy = size // 2
    phase = (phase_bucket / float(ORB_PHASE_BUCKETS)) * math.tau
    pulse = 0.5 + 0.5 * math.sin(phase * 2.0)
    glow_r = 22 + int(3 * pulse)
    pygame.draw.circle(surf, (*color, 34 + int(20 * pulse)), (cx, cy), glow_r + 6)

    if kind == "shield":
        pygame.draw.circle(surf, (*color, 70), (cx, cy), 27 + int(2 * pulse), 2)
        pts = [(cx, cy - 18), (cx + 16, cy - 7), (cx + 12, cy + 14), (cx, cy + 24), (cx - 12, cy + 14), (cx - 16, cy - 7)]
        pygame.draw.polygon(surf, (*color, 225), pts)
        pygame.draw.polygon(surf, (255, 255, 255, 120), [(cx, cy - 11), (cx + 8, cy - 3), (cx + 5, cy + 8), (cx, cy + 14), (cx - 5, cy + 8), (cx - 8, cy - 3)])
        pygame.draw.line(surf, (255, 255, 255, 90), (cx - 10, cy), (cx + 10, cy), 2)
        pygame.draw.line(surf, (255, 255, 255, 90), (cx, cy - 10), (cx, cy + 10), 2)
        for ang in ORB_ARMS_4:
            px = cx + int(math.cos(ang + phase) * 21)
            py = cy + int(math.sin(ang + phase) * 21)
            pygame.draw.circle(surf, (180, 245, 255, 150), (px, py), 2)
    elif kind == "coin":
        pygame.draw.circle(surf, (255, 230, 120, 220), (cx, cy), 16)
        pygame.draw.circle(surf, (255, 250, 180, 230), (cx - 3, cy - 4), 6)
        pygame.draw.arc(surf, (255, 200, 70, 220), (cx - 17, cy - 17, 34, 34), 0.2 + phase, 5.0 + phase, 4)
        for ang in ORB_ARMS_6:
            px = cx + int(math.cos(ang + phase) * 19)
            py = cy + int(math.sin(ang + phase) * 19)
            pygame.draw.line(surf, (255, 235, 160, 160), (cx, cy), (px, py), 1)
    elif kind == "magnet":
        pygame.draw.arc(surf, (255, 255, 255, 230), (cx - 14, cy - 14, 28, 28), math.pi * 0.12 + phase * 0.5, math.pi * 1.22 + phase * 0.5, 6)
        pygame.draw.line(surf, (255, 255, 255, 230), (cx - 14, cy - 6), (cx - 14, cy + 10), 6)
        pygame.draw.line(surf, (255, 255, 255, 230), (cx + 14, cy - 6), (cx + 14, cy + 10), 6)
        for ang in ORB_ARMS_5:
            px = cx + int(math.cos(ang + phase * 1.2) * 18)
            py = cy + int(math.sin(ang + phase * 1.2) * 18)
            pygame.draw.circle(surf, (255, 140, 140, 110), (px, py), 2)
    elif kind == "boost":
        bolt = [(cx - 1, cy - 20), (cx + 12, cy - 5), (cx + 3, cy - 4), (cx + 8, cy + 18), (cx - 14, cy - 1), (cx - 5, cy - 1)]
        pygame.draw.polygon(surf, (255, 255, 255, 235), bolt)
        pygame.draw.circle(surf, (160, 255, 180, 180), (cx, cy), 22, 2)
        for ang in ORB_ARMS_8:
            px = cx + int(math.cos(ang + phase) * 19)
            py = cy + int(math.sin(ang + phase) * 19)
            pygame.draw.line(surf, (180, 255, 200, 100), (cx, cy), (px, py), 1)
    elif kind == "revive":
        ring = 24 + int(2 * pulse)
        pygame.draw.circle(surf, (255, 220, 150, 170), (cx, cy), ring, 3)
        pygame.draw.circle(surf, (255, 248, 220, 220), (cx, cy), 11)
        pygame.draw.polygon(surf, (255, 210, 120, 240), [(cx, cy - 18), (cx + 11, cy - 6), (cx + 5, cy - 6), (cx + 8, cy + 8), (cx, cy + 16), (cx - 8, cy + 8), (cx - 5, cy - 6), (cx - 11, cy - 6)])
        pygame.draw.rect(surf, (120, 70, 30, 220), (cx - 3, cy - 4, 6, 16), border_radius=2)
        pygame.draw.line(surf, (255, 255, 255, 150), (cx - 10, cy - 1), (cx + 10, cy - 1), 2)
        for ang in ORB_ARMS_6:
            px = cx + int(math.cos(ang + phase * 1.5) * (ring - 4))
            py = cy + int(math.sin(ang + phase * 1.5) * (ring - 4))
            pygame.draw.circle(surf, (255, 240, 180, 180), (px, py), 2)
    elif kind == "multiplier":
        pygame.draw.circle(surf, (255, 210, 255, 60), (cx, cy), 23)
        draw_text(surf, get_cached_sysfont("arial", 18, bold=True), "X2", (cx, cy - 10), WHITE, center=True, shadow=False)
        pygame.draw.arc(surf, (255, 210, 255, 200), (cx - 21, cy - 21, 42, 42), phase * 1.2, phase * 1.2 + 4.0, 3)
    elif kind == "core":
        pygame.draw.polygon(surf, (255, 240, 210, 245), [(cx, cy - 20), (cx + 15, cy - 8), (cx + 10, cy + 10), (cx, cy + 20), (cx - 10, cy + 10), (cx - 15, cy - 8)])
        pygame.draw.circle(surf, (255, 140, 90, 220), (cx, cy), 4)
        pygame.draw.circle(surf, (255, 210, 160, 110), (cx, cy), 24, 2)
    else:
        pygame.draw.circle(surf, (*color, 180), (cx, cy), 18)

    for ang in ORB_ARMS_4:
        px = cx + int(math.cos(ang + phase * 1.5) * 28)
        py = cy + int(math.sin(ang + phase * 1.5) * 28)
        pygame.draw.circle(surf, (*color, 120), (px, py), 2)

    _ORB_BODY_CACHE[key] = surf
    _trim_cache(_ORB_BODY_CACHE, 256)
    return surf

class SoundBank:
    def __init__(self):
        self.enabled = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

    def init(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            if not self.sounds:
                self.sounds["flap"] = self._tone(760, 0.07, 0.40)
                self.sounds["score"] = self._tone(1120, 0.08, 0.45)
                self.sounds["hit"] = self._noise_burst(0.16, 0.55)
                self.sounds["power"] = self._tone(520, 0.14, 0.50, add_harmonic=True)
                self.sounds["boss"] = self._tone(180, 0.22, 0.60, add_harmonic=True)
                self.sounds["win"] = self._tone(880, 0.30, 0.45, add_harmonic=True)
                self.sounds["click"] = self._tone(620, 0.05, 0.30)
                self.sounds["glitch"] = self._glitch_sound(0.18, 0.60)
                self.sounds["glitch_hard"] = self._glitch_sound(0.28, 0.90)
                self.sounds["typewriter"] = self._typewriter_sound(0.32)
                self.sounds["egg_ambient"] = self._egg_ambient_sound(1.35, 0.35)
                self.sounds["bsod_shock"] = self._bsod_shock_sound(1.2, 0.98)
                self.sounds["chaos_surge"] = self._chaos_surge_sound(2.2, 0.82)
                self.sounds["static_crackle"] = self._static_crackle_sound(0.10, 0.70)
            self.enabled = True
            try:
                pygame.mixer.unpause()
            except Exception:
                pass
            return True
        except Exception:
            self.enabled = False
            return False

    def _tone(self, freq, duration, volume, add_harmonic=False):
        sr = 44100
        n = max(1, int(sr * duration))
        t = np.linspace(0, duration, n, endpoint=False)
        env = np.exp(-4.5 * t / duration)
        wave = np.sin(2 * np.pi * freq * t)
        if add_harmonic:
            wave += 0.35 * np.sin(2 * np.pi * freq * 2 * t)
            wave += 0.20 * np.sin(2 * np.pi * freq * 3 * t)
        wave *= env
        wave *= volume
        arr = np.asarray(wave * 32767, dtype=np.int16)
        stereo = np.column_stack([arr, arr])
        return pygame.sndarray.make_sound(stereo)

    def _noise_burst(self, duration, volume):
        sr = 44100
        n = max(1, int(sr * duration))
        t = np.linspace(0, duration, n, endpoint=False)
        env = np.exp(-5.5 * t / duration)
        noise = (np.random.rand(n) * 2 - 1) * env * volume
        low = np.sin(2 * np.pi * 120 * t) * 0.20 * env
        wave = noise + low
        arr = np.asarray(wave * 32767, dtype=np.int16)
        stereo = np.column_stack([arr, arr])
        return pygame.sndarray.make_sound(stereo)

    def _glitch_sound(self, duration: float, volume: float):
        """Short static-burst with descending sweep — Easter egg glitch."""
        sr = 44100
        n = max(1, int(sr * duration))
        t = np.linspace(0, duration, n, endpoint=False)
        env = np.exp(-4.0 * t / duration)
        freq_sweep = np.linspace(1100, 180, n)
        phase_acc = np.cumsum(freq_sweep / sr)
        tone = np.sin(2 * np.pi * phase_acc) * 0.55
        noise = (np.random.rand(n) * 2 - 1) * 0.65
        square_mod = np.sign(np.sin(2 * np.pi * 44 * t)) * 0.20
        wave = (tone + noise + square_mod) * env * volume
        arr = np.asarray(np.clip(wave, -1.0, 1.0) * 32767, dtype=np.int16)
        offset = max(1, int(sr * 0.003))
        left = arr
        right = np.concatenate([np.zeros(offset, dtype=np.int16), arr[:-offset]])
        stereo = np.column_stack([left, right])
        return pygame.sndarray.make_sound(stereo)

    def _typewriter_sound(self, volume: float = 0.32):
        """Short percussive click — mechanical key-press for Easter egg typewriter effect."""
        sr = 44100
        n = int(sr * 0.048)
        t = np.linspace(0, 0.048, n, endpoint=False)
        env = np.exp(-110.0 * t)
        wave  = np.sin(2 * np.pi * 3400 * t) * 0.70
        wave += np.sin(2 * np.pi * 1600 * t) * 0.28
        wave += (np.random.rand(n) * 2 - 1) * 0.08
        wave *= env * volume
        arr = np.asarray(np.clip(wave, -1.0, 1.0) * 32767, dtype=np.int16)
        stereo = np.column_stack([arr, arr])
        return pygame.sndarray.make_sound(stereo)

    def _egg_ambient_sound(self, duration: float = 1.35, volume: float = 0.35):
        """Loopable static bed used for the Easter egg ambience — now deeper & more menacing."""
        sr = 44100
        n = max(1, int(sr * duration))
        t = np.linspace(0, duration, n, endpoint=False)
        env = 0.88 + 0.12 * np.sin(2 * np.pi * 0.7 * t)
        hiss  = (np.random.rand(n) * 2 - 1) * 0.60
        crackle = np.sign(np.sin(2 * np.pi * 73 * t)) * 0.12
        # Extra sub-bass growl
        growl = 0.18 * np.sin(2 * np.pi * 48 * t + np.sin(2 * np.pi * 1.2 * t) * 6)
        tone  = 0.10 * np.sin(2 * np.pi * 138 * t) + 0.07 * np.sin(2 * np.pi * 286 * t)
        rumble = 0.08 * np.sin(2 * np.pi * 28 * t)
        wave  = (hiss + crackle + tone + rumble + growl) * env * volume
        arr   = np.asarray(np.clip(wave, -1.0, 1.0) * 32767, dtype=np.int16)
        stereo = np.column_stack([arr, np.roll(arr, 22)])
        return pygame.sndarray.make_sound(stereo)

    def _bsod_shock_sound(self, duration: float = 1.2, volume: float = 0.98):
        """Hard-hitting static wall + deep sub-thud — the BSOD impact."""
        sr = 44100
        n  = max(1, int(sr * duration))
        t  = np.linspace(0, duration, n, endpoint=False)
        # Instant wall of noise — no fade-in
        noise_env = np.exp(-2.8 * t / duration)
        noise_env[:max(1, int(sr * 0.003))] = 1.0
        noise = (np.random.rand(n) * 2 - 1) * noise_env
        # Sub-bass body thud
        thud_env = np.exp(-7.0 * t)
        thud = np.sin(2 * np.pi * 42 * t) * 0.80 * thud_env
        # High-to-low frequency sweep
        freq_sweep = np.linspace(2800, 60, n)
        phase_acc  = np.cumsum(freq_sweep / sr)
        sweep_env  = np.exp(-3.5 * t / duration)
        sweep = np.sin(2 * np.pi * phase_acc) * 0.50 * sweep_env
        # Mid crunch
        crunch_env = np.exp(-9.0 * t)
        crunch = np.sign(np.sin(2 * np.pi * 320 * t)) * 0.25 * crunch_env
        wave = np.clip((noise + thud + sweep + crunch) * volume, -1.0, 1.0)
        arr  = np.asarray(wave * 32767, dtype=np.int16)
        # Slight stereo spread
        offset = max(1, int(sr * 0.005))
        left   = arr
        right  = np.concatenate([np.zeros(offset, dtype=np.int16), arr[:-offset]])
        stereo = np.column_stack([left, right])
        return pygame.sndarray.make_sound(stereo)

    def _chaos_surge_sound(self, duration: float = 2.2, volume: float = 0.82):
        """Rising noise surge for the chaos build-up — swell that peaks hard."""
        sr = 44100
        n  = max(1, int(sr * duration))
        t  = np.linspace(0, duration, n, endpoint=False)
        env = (t / duration) ** 0.55
        noise = (np.random.rand(n) * 2 - 1)
        pulse = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 11 * t))
        thrum = 0.35 * np.sin(2 * np.pi * 68 * t + np.sin(2 * np.pi * 2.2 * t) * 9)
        screech_freq = np.linspace(440, 1800, n)
        phase_acc = np.cumsum(screech_freq / sr)
        screech = 0.20 * np.sin(2 * np.pi * phase_acc) * env
        wave = np.clip((noise * pulse + thrum + screech) * env * volume, -1.0, 1.0)
        arr  = np.asarray(wave * 32767, dtype=np.int16)
        stereo = np.column_stack([arr, np.roll(arr, 33)])
        return pygame.sndarray.make_sound(stereo)

    def _static_crackle_sound(self, duration: float = 0.10, volume: float = 0.70):
        """Sharp static crackle burst — plays frequently during glitch/chaos phases."""
        sr = 44100
        n  = max(1, int(sr * duration))
        t  = np.linspace(0, duration, n, endpoint=False)
        env = np.exp(-18.0 * t)
        noise = (np.random.rand(n) * 2 - 1) * 0.90
        tick  = np.sign(np.sin(2 * np.pi * 580 * t)) * 0.30 * np.exp(-30.0 * t)
        wave  = np.clip((noise + tick) * env * volume, -1.0, 1.0)
        arr   = np.asarray(wave * 32767, dtype=np.int16)
        stereo = np.column_stack([arr, arr])
        return pygame.sndarray.make_sound(stereo)

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def play_loop(self, name: str, volume: float = 1.0):
        if self.enabled and name in self.sounds:
            try:
                channel = self.sounds[name].play(loops=-1)
                if channel is not None:
                    channel.set_volume(volume)
                return channel
            except Exception:
                return None
        return None

    def stop_channel(self, channel):
        try:
            if channel is not None:
                channel.stop()
        except Exception:
            pass

    def stop_all(self):
        if pygame.mixer.get_init():
            try:
                pygame.mixer.stop()
            except Exception:
                pass

    def set_enabled(self, enabled: bool):
        if enabled:
            return self.init()
        self.enabled = False
        self.stop_all()
        return False

@dataclass(slots=True)
class Difficulty:
    name: str
    gravity: float
    flap: float
    pipe_speed: float
    pipe_gap: int
    pipe_interval: float
    power_rate: float
    boss_hp: int
    wind_strength: float
    background_speed: float

DIFFICULTIES = [
    Difficulty("EASY", gravity=1350.0, flap=-430.0, pipe_speed=220.0, pipe_gap=190, pipe_interval=1.62, power_rate=0.26, boss_hp=6, wind_strength=10.0, background_speed=26.0),
    Difficulty("NORMAL", gravity=1500.0, flap=-440.0, pipe_speed=250.0, pipe_gap=165, pipe_interval=1.40, power_rate=0.20, boss_hp=8, wind_strength=16.0, background_speed=33.0),
    Difficulty("HARD", gravity=1650.0, flap=-452.0, pipe_speed=285.0, pipe_gap=142, pipe_interval=1.20, power_rate=0.15, boss_hp=10, wind_strength=24.0, background_speed=40.0),
    Difficulty("INSANE", gravity=1860.0, flap=-454.0, pipe_speed=336.0, pipe_gap=118, pipe_interval=0.95, power_rate=0.08, boss_hp=13, wind_strength=36.0, background_speed=49.0),
]

def boss_item_table(difficulty_name: str, phase: int):
    """Balanced boss-item distribution across difficulties.

    Boss fights should feel rewarding, but not flood the screen with items.
    The overall drop rate is capped more tightly, while the mix stays close
    across modes so rewards remain fair.
    """
    phase = 1 if phase <= 1 else 2 if phase == 2 else 3

    drop_rates = {
        "EASY": (0.58, 0.52, 0.46),
        "NORMAL": (0.52, 0.46, 0.40),
        "HARD": (0.46, 0.40, 0.34),
        "INSANE": (0.36, 0.30, 0.24),
    }
    core_chances = {
        "EASY": (0.34, 0.43, 0.51),
        "NORMAL": (0.31, 0.40, 0.48),
        "HARD": (0.28, 0.36, 0.44),
        "INSANE": (0.22, 0.29, 0.35),
    }
    duo_chances = {
        "EASY": (0.10, 0.16, 0.20),
        "NORMAL": (0.08, 0.13, 0.17),
        "HARD": (0.06, 0.10, 0.13),
        "INSANE": (0.03, 0.05, 0.08),
    }
    trio_chances = {
        "EASY": (0.00, 0.03, 0.05),
        "NORMAL": (0.00, 0.02, 0.03),
        "HARD": (0.00, 0.01, 0.02),
        "INSANE": (0.00, 0.00, 0.01),
    }
    support_tables = {
        "EASY": [
            ("coin", 0.19),
            ("magnet", 0.18),
            ("boost", 0.18),
            ("shield", 0.15),
            ("revive", 0.15),
            ("multiplier", 0.15),
        ],
        "NORMAL": [
            ("coin", 0.20),
            ("magnet", 0.18),
            ("boost", 0.18),
            ("shield", 0.14),
            ("revive", 0.14),
            ("multiplier", 0.16),
        ],
        "HARD": [
            ("coin", 0.21),
            ("magnet", 0.18),
            ("boost", 0.18),
            ("shield", 0.13),
            ("revive", 0.13),
            ("multiplier", 0.17),
        ],
        "INSANE": [
            ("coin", 0.22),
            ("magnet", 0.18),
            ("boost", 0.18),
            ("shield", 0.12),
            ("revive", 0.12),
            ("multiplier", 0.18),
        ],
    }
    name = difficulty_name if difficulty_name in drop_rates else "NORMAL"
    idx = phase - 1
    return {
        "drop_rate": drop_rates[name][idx],
        "core_chance": core_chances[name][idx],
        "duo_chance": duo_chances[name][idx],
        "trio_chance": trio_chances[name][idx],
        "support_table": support_tables[name],
    }

@dataclass(slots=True)
class Skin:
    name: str
    bird_main: Tuple[int, int, int]
    bird_alt: Tuple[int, int, int]
    bird_beak: Tuple[int, int, int]
    trail: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    cost: int = 0
    fx: str = "default"

SKINS: List[Skin] = [
    Skin("CLASSIC", (255, 218, 87), (242, 170, 35), (255, 158, 33), (255, 240, 180), (75, 170, 255), 0, "CLASSIC"),
    Skin("NEON", (132, 245, 255), (30, 180, 255), (255, 255, 255), (100, 255, 220), (255, 88, 196), 80, "NEON"),
    Skin("AQUA", (120, 255, 215), (40, 200, 180), (235, 255, 255), (90, 220, 255), (60, 170, 255), 90, "AQUA"),
    Skin("MINT", (180, 255, 210), (62, 207, 143), (245, 255, 248), (130, 255, 180), (90, 255, 220), 100, "MINT"),
    Skin("CHERRY", (255, 125, 155), (225, 55, 90), (255, 235, 240), (255, 130, 190), (120, 255, 140), 110, "CHERRY"),
    Skin("LAGOON", (124, 228, 255), (58, 154, 230), (240, 255, 255), (92, 230, 210), (72, 170, 255), 120, "LAGOON"),
    Skin("EMBER", (255, 135, 90), (255, 70, 40), (255, 220, 140), (255, 160, 60), (255, 100, 40), 130, "EMBER"),
    Skin("SHADOW", (88, 96, 120), (30, 35, 50), (210, 215, 230), (130, 140, 180), (220, 220, 255), 140, "SHADOW"),
    Skin("VIOLET", (208, 172, 255), (150, 92, 255), (255, 245, 255), (200, 140, 255), (255, 120, 210), 150, "VIOLET"),
    Skin("ROSE", (255, 170, 190), (235, 95, 140), (255, 240, 245), (255, 145, 180), (120, 255, 170), 160, "ROSE"),
    Skin("CRYSTAL", (200, 240, 255), (120, 170, 255), (255, 255, 255), (140, 220, 255), (120, 255, 240), 180, "CRYSTAL"),
    Skin("SOLAR", (255, 238, 130), (255, 176, 54), (255, 255, 200), (255, 220, 100), (255, 145, 60), 200, "SOLAR"),
    Skin("LAVA", (255, 130, 64), (180, 42, 28), (255, 235, 180), (255, 170, 70), (255, 90, 48), 220, "LAVA"),
    Skin("AURORA", (170, 255, 230), (75, 230, 170), (255, 255, 255), (120, 255, 200), (120, 170, 255), 240, "AURORA"),
    Skin("PIXEL", (255, 194, 96), (255, 128, 88), (255, 255, 255), (255, 224, 130), (90, 255, 190), 260, "PIXEL"),
    Skin("FROST", (232, 248, 255), (140, 196, 255), (255, 255, 255), (170, 240, 255), (100, 220, 255), 280, "FROST"),
    Skin("STEEL", (186, 198, 220), (96, 108, 130), (255, 255, 255), (160, 175, 200), (120, 210, 255), 300, "STEEL"),
    Skin("GHOST", (210, 225, 255), (145, 168, 224), (255, 255, 255), (220, 245, 255), (170, 210, 255), 320, "GHOST"),
    Skin("PRISM", (255, 200, 255), (170, 120, 255), (255, 255, 255), (120, 255, 255), (255, 130, 220), 340, "PRISM"),
    Skin("CYBER", (95, 245, 255), (28, 160, 255), (255, 255, 255), (130, 255, 180), (255, 95, 190), 360, "CYBER"),
    Skin("GALAXY", (190, 160, 255), (88, 66, 180), (255, 245, 255), (130, 110, 255), (255, 120, 220), 380, "GALAXY"),
    Skin("VOID", (58, 62, 82), (16, 18, 34), (210, 215, 255), (120, 120, 200), (170, 120, 255), 400, "VOID"),
    Skin("ROYAL", (240, 212, 100), (170, 105, 35), (255, 245, 200), (255, 225, 120), (120, 75, 255), 420, "ROYAL"),
    Skin("SAND", (255, 235, 160), (220, 190, 110), (255, 250, 220), (255, 220, 130), (190, 145, 70), 440, "SAND"),
    Skin("CORAL", (255, 170, 132), (255, 100, 92), (255, 250, 220), (255, 190, 160), (100, 230, 210), 460, "CORAL"),
]

BOSS_SPECS = [
    {
        "name": "Aegis Core",
        "short": "Aegis",
        "accent": (255, 96, 118),
        "core": (255, 220, 162),
        "dark": (26, 30, 44),
        "body": (76, 78, 100),
        "hp_mult": 1.00,
        "attack": "aegis",
        "projectile": "aegis",
        "art": "aegis",
        "description": "steady shields and fair openings",
        "periods": {"EASY": (2.18, 1.42), "NORMAL": (1.96, 1.22), "HARD": (1.76, 1.04)},
        "speeds": {"EASY": 136, "NORMAL": 148, "HARD": 160},
    },
    {
        "name": "Tempest",
        "short": "Tempest",
        "accent": (108, 224, 255),
        "core": (230, 250, 255),
        "dark": (18, 30, 46),
        "body": (62, 96, 134),
        "hp_mult": 1.10,
        "attack": "tempest",
        "projectile": "tempest",
        "art": "tempest",
        "description": "wind-lashed spreads and pressure lanes",
        "periods": {"EASY": (2.05, 1.30), "NORMAL": (1.84, 1.10), "HARD": (1.62, 0.96)},
        "speeds": {"EASY": 142, "NORMAL": 154, "HARD": 168},
    },
    {
        "name": "Void Regent",
        "short": "Void",
        "accent": (190, 130, 255),
        "core": (248, 236, 255),
        "dark": (18, 18, 30),
        "body": (58, 56, 88),
        "hp_mult": 1.22,
        "attack": "void",
        "projectile": "void",
        "art": "void",
        "description": "spirals, fades, and sudden bursts",
        "periods": {"EASY": (1.96, 1.22), "NORMAL": (1.74, 1.02), "HARD": (1.52, 0.88)},
        "speeds": {"EASY": 150, "NORMAL": 162, "HARD": 174},
    },
    {
        "name": "Chrono Bastion",
        "short": "Chrono",
        "accent": (255, 198, 108),
        "core": (255, 244, 218),
        "dark": (54, 30, 18),
        "body": (146, 94, 48),
        "hp_mult": 1.34,
        "attack": "chrono",
        "projectile": "chrono",
        "art": "chrono",
        "description": "time-bending volleys and gear traps",
        "periods": {"EASY": (1.86, 1.12), "NORMAL": (1.64, 0.94), "HARD": (1.44, 0.82)},
        "speeds": {"EASY": 156, "NORMAL": 168, "HARD": 180},
    },
    {
        "name": "Prism Nexus",
        "short": "Prism",
        "accent": (150, 255, 214),
        "core": (244, 255, 250),
        "dark": (12, 58, 44),
        "body": (50, 188, 148),
        "hp_mult": 1.46,
        "attack": "prism",
        "projectile": "prism",
        "art": "prism",
        "description": "split beams and prismatic angles",
        "periods": {"EASY": (1.78, 1.08), "NORMAL": (1.56, 0.90), "HARD": (1.34, 0.78)},
        "speeds": {"EASY": 160, "NORMAL": 172, "HARD": 184},
    },
    {
        "name": "Verdant Bloom",
        "short": "Bloom",
        "accent": (128, 255, 168),
        "core": (242, 255, 242),
        "dark": (24, 52, 26),
        "body": (74, 150, 84),
        "hp_mult": 1.58,
        "attack": "bloom",
        "projectile": "bloom",
        "art": "bloom",
        "description": "seed arcs and vine-like pressure",
        "periods": {"EASY": (1.72, 1.02), "NORMAL": (1.50, 0.86), "HARD": (1.30, 0.74)},
        "speeds": {"EASY": 144, "NORMAL": 156, "HARD": 170},
    },
    {
        "name": "Ember Warden",
        "short": "Ember",
        "accent": (255, 134, 84),
        "core": (255, 236, 180),
        "dark": (74, 24, 18),
        "body": (176, 78, 46),
        "hp_mult": 1.70,
        "attack": "ember",
        "projectile": "ember",
        "art": "ember",
        "description": "meteors, sparks, and heat waves",
        "periods": {"EASY": (1.68, 0.98), "NORMAL": (1.46, 0.82), "HARD": (1.24, 0.72)},
        "speeds": {"EASY": 156, "NORMAL": 170, "HARD": 184},
    },
    {
        "name": "Tide Oracle",
        "short": "Tide",
        "accent": (98, 214, 255),
        "core": (240, 252, 255),
        "dark": (18, 52, 72),
        "body": (46, 122, 156),
        "hp_mult": 1.82,
        "attack": "tide",
        "projectile": "tide",
        "art": "tide",
        "description": "wave pulses and drifting currents",
        "periods": {"EASY": (1.62, 0.94), "NORMAL": (1.40, 0.80), "HARD": (1.20, 0.68)},
        "speeds": {"EASY": 148, "NORMAL": 160, "HARD": 172},
    },
    {
        "name": "Frost Citadel",
        "short": "Frost",
        "accent": (190, 238, 255),
        "core": (255, 255, 255),
        "dark": (26, 46, 72),
        "body": (120, 166, 214),
        "hp_mult": 1.92,
        "attack": "frost",
        "projectile": "frost",
        "art": "frost",
        "description": "glacial shards with measured gaps",
        "periods": {"EASY": (1.58, 0.90), "NORMAL": (1.36, 0.76), "HARD": (1.16, 0.64)},
        "speeds": {"EASY": 152, "NORMAL": 164, "HARD": 176},
    },
    {
        "name": "Stellar Forge",
        "short": "Stellar",
        "accent": (255, 220, 120),
        "core": (255, 250, 220),
        "dark": (48, 36, 18),
        "body": (164, 122, 64),
        "hp_mult": 2.02,
        "attack": "stellar",
        "projectile": "stellar",
        "art": "stellar",
        "description": "starbursts and orbiting pressure",
        "periods": {"EASY": (1.52, 0.86), "NORMAL": (1.30, 0.72), "HARD": (1.12, 0.62)},
        "speeds": {"EASY": 160, "NORMAL": 174, "HARD": 186},
    },
    {
        "name": "Obsidian Seraph",
        "short": "Obsidian",
        "accent": (186, 138, 255),
        "core": (248, 240, 255),
        "dark": (18, 16, 28),
        "body": (66, 62, 88),
        "hp_mult": 2.12,
        "attack": "obsidian",
        "projectile": "obsidian",
        "art": "obsidian",
        "description": "heavy cuts with dark angles",
        "periods": {"EASY": (1.48, 0.84), "NORMAL": (1.26, 0.70), "HARD": (1.08, 0.60)},
        "speeds": {"EASY": 166, "NORMAL": 178, "HARD": 190},
    },
    {
        "name": "Aurora Heart",
        "short": "Aurora",
        "accent": (132, 255, 232),
        "core": (255, 255, 255),
        "dark": (18, 58, 64),
        "body": (62, 176, 156),
        "hp_mult": 2.24,
        "attack": "aurora",
        "projectile": "aurora",
        "art": "aurora",
        "description": "ribbons of light and calm pressure",
        "periods": {"EASY": (1.44, 0.82), "NORMAL": (1.22, 0.68), "HARD": (1.04, 0.58)},
        "speeds": {"EASY": 154, "NORMAL": 168, "HARD": 180},
    },
    {
        "name": "Nova Crown",
        "short": "Nova",
        "accent": (255, 214, 120),
        "core": (255, 248, 232),
        "dark": (52, 30, 76),
        "body": (118, 84, 162),
        "hp_mult": 2.34,
        "attack": "nova",
        "projectile": "nova",
        "art": "nova",
        "description": "orbiting bursts and fair openings",
        "periods": {"EASY": (1.40, 0.80), "NORMAL": (1.20, 0.66), "HARD": (1.02, 0.56)},
        "speeds": {"EASY": 160, "NORMAL": 174, "HARD": 186},
    },
    {
        "name": "Rift Monarch",
        "short": "Rift",
        "accent": (145, 116, 255),
        "core": (248, 240, 255),
        "dark": (18, 14, 36),
        "body": (72, 54, 112),
        "hp_mult": 2.46,
        "attack": "rift",
        "projectile": "rift",
        "art": "rift",
        "description": "tear lanes and shifting angles",
        "periods": {"EASY": (1.36, 0.78), "NORMAL": (1.16, 0.64), "HARD": (0.98, 0.54)},
        "speeds": {"EASY": 164, "NORMAL": 178, "HARD": 190},
    },
    {
        "name": "Thorn Sovereign",
        "short": "Thorn",
        "accent": (126, 255, 150),
        "core": (242, 255, 242),
        "dark": (24, 56, 24),
        "body": (66, 128, 74),
        "hp_mult": 2.58,
        "attack": "thorn",
        "projectile": "thorn",
        "art": "thorn",
        "description": "vine sweeps and growing pressure",
        "periods": {"EASY": (1.32, 0.76), "NORMAL": (1.12, 0.62), "HARD": (0.94, 0.52)},
        "speeds": {"EASY": 154, "NORMAL": 168, "HARD": 180},
    },
    {
        "name": "Sentinel Prism",
        "short": "Sentinel",
        "accent": (220, 234, 255),
        "core": (255, 255, 255),
        "dark": (22, 36, 66),
        "body": (116, 148, 190),
        "hp_mult": 2.70,
        "attack": "sentinel",
        "projectile": "sentinel",
        "art": "sentinel",
        "description": "rotating shields and measured bursts",
        "periods": {"EASY": (1.28, 0.74), "NORMAL": (1.08, 0.60), "HARD": (0.90, 0.50)},
        "speeds": {"EASY": 166, "NORMAL": 180, "HARD": 192},
    },
    {
        "name": "HELL",
        "short": "HELL",
        "accent": (255, 124, 72),
        "core": (255, 238, 198),
        "dark": (72, 16, 14),
        "body": (186, 58, 34),
        "hp_mult": 3.20,
        "attack": "ember",
        "projectile": "ember",
        "art": "ember",
        "description": "infernal barrage and soul-fire pressure",
        "periods": {"EASY": (1.08, 0.64), "NORMAL": (0.92, 0.54), "HARD": (0.76, 0.44)},
        "speeds": {"EASY": 176, "NORMAL": 190, "HARD": 204},
    },
]

VISIBLE_BOSS_INDICES = [i for i, spec in enumerate(BOSS_SPECS) if spec.get("short") != "HELL"]

BOSS_THEMES = [
    {
        "name": "Aegis Core",
        "sky_top": (12, 22, 48),
        "sky_bottom": (78, 120, 186),
        "haze": (255, 212, 136),
        "pipe": (86, 112, 174),
        "pipe_dark": (24, 38, 60),
        "cloud": (220, 226, 242),
        "ground": (28, 42, 66),
        "bg_kind": "aegis",
    },
    {
        "name": "Tempest",
        "sky_top": (6, 30, 54),
        "sky_bottom": (18, 170, 198),
        "haze": (108, 246, 240),
        "pipe": (46, 188, 224),
        "pipe_dark": (12, 82, 112),
        "cloud": (214, 246, 252),
        "ground": (12, 58, 74),
        "bg_kind": "tempest",
    },
    {
        "name": "Void Regent",
        "sky_top": (5, 6, 16),
        "sky_bottom": (58, 18, 92),
        "haze": (205, 136, 255),
        "pipe": (100, 82, 154),
        "pipe_dark": (20, 18, 34),
        "cloud": (232, 220, 255),
        "ground": (18, 12, 30),
        "bg_kind": "void",
    },
    {
        "name": "Chrono Bastion",
        "sky_top": (36, 20, 8),
        "sky_bottom": (192, 124, 52),
        "haze": (255, 190, 118),
        "pipe": (196, 122, 58),
        "pipe_dark": (92, 52, 18),
        "cloud": (252, 232, 210),
        "ground": (62, 34, 18),
        "bg_kind": "chrono",
    },
    {
        "name": "Prism Nexus",
        "sky_top": (8, 34, 24),
        "sky_bottom": (40, 164, 120),
        "haze": (150, 255, 214),
        "pipe": (52, 188, 148),
        "pipe_dark": (10, 88, 66),
        "cloud": (224, 255, 244),
        "ground": (14, 58, 44),
        "bg_kind": "prism",
    },
    {
        "name": "Verdant Bloom",
        "sky_top": (10, 34, 14),
        "sky_bottom": (70, 146, 72),
        "haze": (128, 255, 168),
        "pipe": (86, 174, 90),
        "pipe_dark": (24, 70, 32),
        "cloud": (236, 255, 238),
        "ground": (24, 66, 26),
        "bg_kind": "bloom",
    },
    {
        "name": "Ember Warden",
        "sky_top": (74, 18, 14),
        "sky_bottom": (214, 104, 46),
        "haze": (255, 156, 88),
        "pipe": (214, 96, 42),
        "pipe_dark": (104, 36, 26),
        "cloud": (255, 234, 212),
        "ground": (86, 34, 22),
        "bg_kind": "ember",
    },
    {
        "name": "Tide Oracle",
        "sky_top": (8, 34, 54),
        "sky_bottom": (24, 138, 178),
        "haze": (108, 228, 255),
        "pipe": (64, 170, 208),
        "pipe_dark": (16, 78, 112),
        "cloud": (230, 250, 255),
        "ground": (14, 60, 84),
        "bg_kind": "tide",
    },
    {
        "name": "Frost Citadel",
        "sky_top": (12, 24, 52),
        "sky_bottom": (82, 146, 214),
        "haze": (190, 238, 255),
        "pipe": (116, 172, 224),
        "pipe_dark": (30, 58, 92),
        "cloud": (245, 251, 255),
        "ground": (22, 52, 84),
        "bg_kind": "frost",
    },
    {
        "name": "Stellar Forge",
        "sky_top": (8, 10, 22),
        "sky_bottom": (72, 42, 108),
        "haze": (255, 220, 120),
        "pipe": (126, 92, 182),
        "pipe_dark": (24, 18, 42),
        "cloud": (238, 224, 255),
        "ground": (22, 16, 38),
        "bg_kind": "stellar",
    },
    {
        "name": "Obsidian Seraph",
        "sky_top": (4, 4, 10),
        "sky_bottom": (52, 26, 72),
        "haze": (186, 138, 255),
        "pipe": (92, 72, 124),
        "pipe_dark": (14, 12, 24),
        "cloud": (240, 230, 255),
        "ground": (14, 10, 24),
        "bg_kind": "obsidian",
    },
    {
        "name": "Aurora Heart",
        "sky_top": (10, 32, 60),
        "sky_bottom": (36, 176, 164),
        "haze": (132, 255, 232),
        "pipe": (58, 182, 160),
        "pipe_dark": (16, 82, 74),
        "cloud": (235, 255, 255),
        "ground": (14, 60, 60),
        "bg_kind": "aurora",
    },
    {
        "name": "Nova Crown",
        "sky_top": (22, 10, 42),
        "sky_bottom": (108, 54, 164),
        "haze": (255, 212, 120),
        "pipe": (136, 92, 186),
        "pipe_dark": (34, 20, 58),
        "cloud": (245, 236, 255),
        "ground": (30, 18, 50),
        "bg_kind": "nova",
    },
    {
        "name": "Rift Monarch",
        "sky_top": (8, 8, 24),
        "sky_bottom": (58, 24, 98),
        "haze": (145, 116, 255),
        "pipe": (100, 78, 166),
        "pipe_dark": (18, 14, 34),
        "cloud": (240, 232, 255),
        "ground": (16, 12, 28),
        "bg_kind": "rift",
    },
    {
        "name": "Thorn Sovereign",
        "sky_top": (8, 26, 10),
        "sky_bottom": (66, 138, 66),
        "haze": (126, 255, 150),
        "pipe": (92, 178, 100),
        "pipe_dark": (24, 66, 28),
        "cloud": (240, 255, 240),
        "ground": (22, 58, 22),
        "bg_kind": "thorn",
    },
    {
        "name": "Sentinel Prism",
        "sky_top": (10, 18, 42),
        "sky_bottom": (84, 128, 186),
        "haze": (220, 234, 255),
        "pipe": (118, 150, 194),
        "pipe_dark": (24, 38, 64),
        "cloud": (250, 252, 255),
        "ground": (18, 30, 52),
        "bg_kind": "sentinel",
    },
    {
        "name": "HELL",
        "sky_top": (42, 0, 0),
        "sky_bottom": (214, 52, 20),
        "haze": (255, 138, 78),
        "pipe": (255, 110, 46),
        "pipe_dark": (96, 10, 10),
        "cloud": (255, 236, 196),
        "ground": (74, 16, 14),
        "bg_kind": "hell",
    },
]

THEMES = [
    {
        "name": "DAWN",
        "sky_top": (71, 128, 255),
        "sky_bottom": (215, 238, 255),
        "haze": (255, 218, 170),
        "pipe": (69, 181, 86),
        "pipe_dark": (36, 108, 52),
        "cloud": (255, 255, 255),
        "ground": (235, 196, 125),
    },
    {
        "name": "NIGHT",
        "sky_top": (15, 20, 38),
        "sky_bottom": (43, 68, 112),
        "haze": (108, 125, 190),
        "pipe": (71, 145, 210),
        "pipe_dark": (27, 76, 130),
        "cloud": (230, 240, 255),
        "ground": (55, 74, 94),
    },
    {
        "name": "EMBER",
        "sky_top": (72, 21, 18),
        "sky_bottom": (210, 120, 68),
        "haze": (255, 181, 110),
        "pipe": (212, 94, 57),
        "pipe_dark": (120, 40, 30),
        "cloud": (255, 221, 200),
        "ground": (96, 44, 38),
    },
    {
        "name": "AURORA",
        "sky_top": (18, 38, 68),
        "sky_bottom": (32, 150, 158),
        "haze": (122, 255, 224),
        "pipe": (72, 208, 180),
        "pipe_dark": (20, 116, 120),
        "cloud": (235, 255, 255),
        "ground": (22, 68, 72),
    },
]

def draw_boss_background(surf: pygame.Surface, theme: dict, bg_kind: str, t: float):
    cloud = theme["cloud"]
    haze = theme["haze"]
    pipe = theme["pipe"]
    pipe_dark = theme["pipe_dark"]
    ground = theme["ground"]

    def ground_band(height: int = 72):
        pygame.draw.rect(surf, ground, (0, HEIGHT - height, WIDTH, height))
        pygame.draw.rect(surf, pipe, (0, HEIGHT - height, WIDTH, 10))

    # Shared boss-mode pressure layer: every boss gets a more cinematic,
    # more readable silhouette treatment before the per-boss theme details.
    boss_energy = get_clear_surface((WIDTH, HEIGHT), ("boss_energy", bg_kind))
    for i in range(4):
        radius = 112 + i * 58
        alpha = 18 + i * 10
        pygame.draw.circle(boss_energy, (*haze, alpha), (WIDTH // 2, 118), radius, 2 if i < 3 else 1)
    for i in range(14):
        ang = t * (0.55 + i * 0.03) + i * (math.tau / 14)
        length = 94 + i * 6 + int(12 * math.sin(t * 1.8 + i))
        px = WIDTH // 2 + int(math.cos(ang) * length)
        py = 118 + int(math.sin(ang) * length * 0.68)
        pygame.draw.line(boss_energy, (*pipe, 26 + (i % 4) * 5), (WIDTH // 2, 118), (px, py), 1)
    for i in range(18):
        x = (i * 61 + int(t * 110)) % (WIDTH + 120) - 60
        y = 42 + (i % 5) * 14 + int(math.sin(t * 4.0 + i) * 4)
        pygame.draw.circle(boss_energy, (*cloud, 72), (x, y), 2)
    surf.blit(boss_energy, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ─── HELL ───────────────────────────────────────────────────────────────
    # Dense hellscape: lava cracks, towering fire pillars, ember rain,
    # smoke columns, ground spikes, hellfire burst arcs.
    if bg_kind == "hell":
        # Lava-cracked ground
        pygame.draw.rect(surf, ground, (0, HEIGHT - 92, WIDTH, 92))
        for i in range(9):
            lx = 38 + i * 106 + int(math.sin(t * 0.3 + i) * 8)
            pygame.draw.line(surf, (220, 56, 10), (lx, HEIGHT - 92), (lx + 22, HEIGHT - 32), 4)
            pygame.draw.line(surf, (255, 110, 20), (lx + 10, HEIGHT - 82), (lx + 34, HEIGHT - 28), 2)
        # Lava glow pools
        for i in range(6):
            lx = 70 + i * 162
            pygame.draw.ellipse(surf, (220, 52, 8), (lx - 22, HEIGHT - 36, 44, 14))
            pygame.draw.ellipse(surf, (255, 130, 30), (lx - 10, HEIGHT - 32, 20, 7))
        # Hellfire pillars (animated)
        for i in range(14):
            x = (i * 72 + int(t * 56)) % (WIDTH + 110) - 55
            wob = int(math.sin(t * 5.2 + i * 0.9) * 9)
            fh = 36 + (i % 5) * 20 + int((math.sin(t * 4.0 + i) + 1) * 14)
            pygame.draw.polygon(surf, pipe_dark,
                [(x, HEIGHT - 92), (x + 48, HEIGHT - 92),
                 (x + 30 + wob, HEIGHT - 92 - fh),
                 (x - 8 + wob, HEIGHT - 92 - fh + 18)])
            pygame.draw.polygon(surf, haze,
                [(x + 13, HEIGHT - 96), (x + 30 + wob // 2, HEIGHT - 92 - fh // 2),
                 (x + 7 + wob // 2, HEIGHT - 108 - fh // 2), (x - 3, HEIGHT - 98)])
            pygame.draw.polygon(surf, (255, 255, 200),
                [(x + 19, HEIGHT - 100), (x + 26 + wob // 3, HEIGHT - 94 - fh // 3),
                 (x + 14, HEIGHT - 102)])
        # Smoke columns drifting upward
        for i in range(5):
            sx = (i * 198 + int(t * 16)) % (WIDTH + 90) - 45
            for sy in range(HEIGHT - 130, 40, -36):
                fade = int(55 * (HEIGHT - sy) / HEIGHT)
                pygame.draw.circle(surf, (pipe_dark[0] // 3, pipe_dark[1] // 3, pipe_dark[2] // 3),
                                   (sx + int(math.sin(t * 0.9 + i + sy * 0.02) * 8), sy), 16)
        # Floating ember sparks
        for i in range(80):
            x = (i * 43 + int(t * 30)) % WIDTH
            y = (i * 67 + int(t * 20)) % (HEIGHT - 120) + 18
            pygame.draw.circle(surf, cloud, (x, y), 1)
        # Hell arc ornaments in sky
        for i in range(8):
            x = 48 + i * 118 + int(math.sin(t * 1.0 + i) * 18)
            y = 32 + int((math.sin(t * 3.6 + i * 0.5) + 1) * 22)
            pygame.draw.arc(surf, haze, (x - 52, y - 20, 124, 72), 0.1, 3.0, 4)
            pygame.draw.arc(surf, pipe_dark, (x - 36, y - 10, 98, 48), 0.2, 2.8, 2)
        # Sky hellfire sparks
        for i in range(22):
            x = 48 + i * 44 + int(math.sin(t * 5.0 + i) * 7)
            y = 40 + int((math.sin(t * 5.4 + i * 1.0) + 1) * 26)
            pygame.draw.circle(surf, haze, (x, y), 2)
            pygame.draw.circle(surf, pipe, (x, y), 5, 1)
        pygame.draw.rect(surf, pipe_dark, (0, HEIGHT - 12, WIDTH, 12))
        # Ground spikes
        for i in range(16):
            x = i * 64 + int(math.sin(t * 1.1 + i) * 10)
            tip = 24 + int((math.sin(t * 2.8 + i * 0.5) + 1) * 12)
            pygame.draw.polygon(surf, pipe, [(x, HEIGHT - 92), (x + 28, HEIGHT - 92), (x + 14, HEIGHT - 92 - tip)])
            pygame.draw.polygon(surf, haze, [(x + 14, HEIGHT - 104), (x + 19, HEIGHT - 92 - tip + 10), (x + 9, HEIGHT - 92 - tip + 10)])
        # HELL-exclusive surge: extra inferno crowns and drifting cinders so the
        # background feels more brutal than the standard Ember theme.
        for i in range(7):
            sx = 58 + i * 132 + int(math.sin(t * 0.75 + i) * 18)
            sy = 30 + int(math.sin(t * 1.6 + i * 0.9) * 10)
            pygame.draw.arc(surf, (255, 180, 80), (sx - 52, sy, 124, 74), 0.12, 2.88, 2)
            pygame.draw.arc(surf, (120, 18, 14), (sx - 30, sy + 12, 88, 42), 0.2, 2.62, 2)
        for i in range(20):
            x = (i * 49 + int(t * 62)) % (WIDTH + 120) - 60
            y = 18 + (i % 5) * 18 + int(math.sin(t * 3.4 + i) * 6)
            pygame.draw.circle(surf, cloud if i % 2 else haze, (x, y), 2)
        return

    # ─── AEGIS ──────────────────────────────────────────────────────────────
    # Hexagonal shield grid, rotating energy rings, shield-node lattice,
    # floating hexagonal shield fragments, energy cross-beams.
    if bg_kind == "aegis":
        # Hexagonal grid background
        for row in range(5):
            for col in range(11):
                hx = 44 + col * 88 + (row % 2) * 44 + int(math.sin(t * 0.35 + col * 0.28) * 4)
                hy = 26 + row * 50
                r = 26
                pts = [(int(hx + r * math.cos(math.pi / 6 + k * math.pi / 3)),
                         int(hy + r * math.sin(math.pi / 6 + k * math.pi / 3))) for k in range(6)]
                pygame.draw.polygon(surf, pipe_dark, pts, 1)
        # Rotating shield arcs (3 stations across top)
        for si in range(3):
            scx = 170 + si * 310
            scy = 76
            for sr in range(3):
                rs = 34 + sr * 16
                arc_s = t * (0.9 + si * 0.25 + sr * 0.12) + si * 1.1
                pygame.draw.arc(surf, haze, (scx - rs, scy - rs, rs * 2, rs * 2),
                                arc_s, arc_s + 3.8, 3 if sr == 0 else 2)
        # Shield-node ring markers
        for i in range(8):
            x = 68 + i * 118 + int(math.sin(t * 0.8 + i) * 12)
            y = 66 + (i % 2) * 34
            pygame.draw.circle(surf, haze, (x, y), 20, 2)
            pygame.draw.line(surf, pipe, (x - 16, y), (x + 16, y), 2)
            pygame.draw.line(surf, pipe, (x, y - 16), (x, y + 16), 2)
            pygame.draw.circle(surf, cloud, (x, y), 4)
        # Floating hexagonal shield fragments
        for i in range(5):
            x = 90 + i * 186 + int(math.sin(t * 0.6 + i) * 16)
            y = 22 + (i % 2) * 22
            pts = [(x, y + 22), (x + 22, y + 6), (x + 44, y + 22),
                   (x + 36, y + 48), (x + 8, y + 52), (x - 4, y + 30)]
            pygame.draw.polygon(surf, pipe_dark, pts)
            pygame.draw.polygon(surf, cloud,
                [(x + 8, y + 14), (x + 26, y + 10), (x + 32, y + 26), (x + 14, y + 34), (x + 2, y + 20)], 1)
        # Energy cross-beams (horizontal streaks)
        for i in range(3):
            bx = 150 + i * 330
            pygame.draw.line(surf, haze, (0, HEIGHT // 3 + i * 18), (WIDTH, HEIGHT // 3 + i * 20), 1)
        ground_band(76)
        return

    # ─── TEMPEST ────────────────────────────────────────────────────────────
    # Stormy: lightning zigzag bolts, spinning wind vortexes,
    # heavy diagonal rain streaks, thick arc storm-clouds.
    if bg_kind == "tempest":
        # Heavy diagonal rain streaks
        for i in range(40):
            x = (i * 36 + int(t * 58)) % (WIDTH + 150) - 75
            pygame.draw.line(surf, pipe, (x, 0), (x + 30, HEIGHT), 1)
        # Wind vortex swirls (3 across)
        for v in range(3):
            vx = 156 + v * 324 + int(math.sin(t * 0.7 + v) * 20)
            vy = 78 + (v % 2) * 38
            for s in range(6):
                rv = 18 + s * 14
                sa = t * (1.3 + s * 0.16) + v * 1.3
                pygame.draw.arc(surf, cloud, (vx - rv, vy - rv, rv * 2, rv * 2),
                                sa, sa + 1.8, 2 if s < 4 else 1)
        # Thick storm arc clouds
        for i in range(8):
            x = (i * 148 + int(t * 36)) % (WIDTH + 210) - 105
            y = 44 + (i % 3) * 38 + int(math.sin(t * 1.4 + i) * 10)
            pygame.draw.arc(surf, cloud, (x, y, 196, 62), 0.08, 3.14, 6)
            pygame.draw.arc(surf, haze, (x + 16, y + 12, 158, 38), 0.2, 2.95, 2)
        # Lightning zigzag bolts
        for lb in range(5):
            bx = 88 + lb * 196 + int(math.sin(t * 0.8 + lb) * 14)
            prev = (bx, 6)
            for seg in range(8):
                ny = prev[1] + 26 + (seg % 2) * 10
                nx = bx + int(math.sin(t * 4.2 + lb * 2.1 + seg * 1.3) * 24)
                pygame.draw.line(surf, cloud, prev, (nx, ny), 2)
                pygame.draw.line(surf, haze, (prev[0] - 1, prev[1]), (nx - 1, ny), 1)
                prev = (nx, ny)
                if ny > 190:
                    break
        # Tall lightning streaks at sides and top
        for i in range(4):
            x = 72 + i * 278 + int(math.sin(t * 1.4 + i) * 22)
            pygame.draw.line(surf, cloud, (x, 4), (x + 26, 100), 3)
        ground_band(68)
        return

    # ─── VOID ───────────────────────────────────────────────────────────────
    # Deep-space: star field, multi-ring void portal, spiraling arms,
    # floating diamond shards, void tendril lines from edges.
    if bg_kind == "void":
        # Dense star field
        for i in range(140):
            x = (i * 29 + int(t * 11)) % WIDTH
            y = (i * 53 + int(t * 8)) % (HEIGHT - 46) + 18
            pygame.draw.circle(surf, cloud, (x, y), 1)
        # Brighter accent stars
        for i in range(18):
            x = (i * 59 + int(t * 7)) % WIDTH
            y = (i * 71 + int(t * 5)) % (HEIGHT // 2) + 14
            pygame.draw.circle(surf, cloud, (x, y), 2)
        # Void portal concentric rings
        center = (WIDTH // 2, 108)
        for off in (0, 14, 28, 44, 58):
            rs = 46 + off
            pygame.draw.circle(surf, haze, center, rs, 2 if off < 44 else 1)
        # Four spiraling arms
        for arm in range(4):
            arm_start = t * (0.55 + arm * 0.14) + arm * (math.tau / 4)
            for seg in range(14):
                ang = arm_start + seg * 0.38
                r1 = 48 + seg * 9
                r2 = 48 + (seg + 1) * 9
                x1 = center[0] + int(math.cos(ang) * r1)
                y1 = center[1] + int(math.sin(ang) * r1)
                x2 = center[0] + int(math.cos(ang + 0.38) * r2)
                y2 = center[1] + int(math.sin(ang + 0.38) * r2)
                pygame.draw.line(surf, haze, (x1, y1), (x2, y2), 2)
        # Floating void shards (diamonds)
        for i in range(12):
            x = 64 + i * 80 + int(math.sin(t * 0.55 + i) * 14)
            y = 26 + (i % 4) * 38 + int(math.cos(t * 0.85 + i) * 10)
            s = 8 + (i % 3) * 4
            pts = [(x, y - s), (x + s, y), (x, y + s), (x - s, y)]
            pygame.draw.polygon(surf, pipe_dark, pts)
            pygame.draw.polygon(surf, haze, pts, 1)
        # Void tendrils from screen edges
        for i in range(6):
            ex = (i % 2) * (WIDTH - 60) + 30
            ey = 38 + i * 68 + int(math.sin(t * 0.8 + i) * 12)
            dx = WIDTH // 2 - ex
            pygame.draw.line(surf, haze, (ex, ey),
                (ex + int(dx * 0.4), ey + int(math.sin(t * 1.5 + i) * 5)), 1)
        # Horizontal marker bands
        for y in (52, 86, 168, 202):
            pygame.draw.line(surf, pipe_dark, (0, y), (WIDTH, y), 1)
        ground_band(70)
        return

    # ─── CHRONO ─────────────────────────────────────────────────────────────
    # Living clockwork: gear-tooth top edge, 4 animated clock faces,
    # pendulum arcs, gear columns, falling gear particles.
    if bg_kind == "chrono":
        # Gear-tooth serration along top edge
        for i in range(32):
            x = i * 30
            pygame.draw.rect(surf, pipe_dark, (x, 0, 18, 14 + (i % 2) * 8))
        # Animated clock faces (4 across)
        for ci in range(4):
            cx = 96 + ci * 256 + int(math.sin(t * 0.4 + ci) * 10)
            cy = 82
            # Outer ring + face
            pygame.draw.circle(surf, pipe, (cx, cy), 32, 3)
            pygame.draw.circle(surf, haze, (cx, cy), 28, 1)
            pygame.draw.circle(surf, cloud, (cx, cy), 5)
            # Hour markers
            for m in range(12):
                ang = m * (math.tau / 12)
                mx = cx + int(math.cos(ang) * 26)
                my = cy + int(math.sin(ang) * 26)
                pygame.draw.circle(surf, pipe_dark, (mx, my), 3 if m % 3 == 0 else 1)
            # Clock hands
            ha = t * (0.38 + ci * 0.08)
            ma = t * (1.5 + ci * 0.18)
            pygame.draw.line(surf, cloud, (cx, cy), (cx + int(math.cos(ha) * 18), cy + int(math.sin(ha) * 18)), 3)
            pygame.draw.line(surf, haze,  (cx, cy), (cx + int(math.cos(ma) * 25), cy + int(math.sin(ma) * 25)), 2)
        # Gear columns
        for i in range(10):
            x = 88 + i * 86 + int(math.sin(t * 1.3 + i) * 10)
            pygame.draw.line(surf, pipe_dark, (x, 148), (x, HEIGHT - 86), 3)
            pygame.draw.rect(surf, pipe, (x - 8, HEIGHT - 94, 16, 18))
            pygame.draw.rect(surf, haze, (x - 4, HEIGHT - 92, 8, 14))
        # Pendulum swings (3 pendulums)
        for p in range(3):
            px = 96 + p * 384
            pa = math.sin(t * (1.1 + p * 0.22)) * 0.95
            ex = px + int(math.sin(pa) * 82)
            ey = 224
            pygame.draw.line(surf, pipe, (px, 28), (ex, ey), 2)
            pygame.draw.circle(surf, haze, (ex, ey), 9)
            pygame.draw.circle(surf, cloud, (ex, ey), 4)
        # Falling micro-gear particles
        for i in range(16):
            gx = (i * 64 + int(t * 28)) % WIDTH
            gy = (i * 43 + int(t * 38)) % (HEIGHT - 110) + 28
            pygame.draw.line(surf, pipe_dark, (gx - 5, gy - 5), (gx + 5, gy - 5), 1)
            pygame.draw.line(surf, pipe_dark, (gx + 5, gy - 5), (gx + 5, gy + 5), 1)
            pygame.draw.line(surf, pipe_dark, (gx + 5, gy + 5), (gx - 5, gy + 5), 1)
            pygame.draw.line(surf, pipe_dark, (gx - 5, gy + 5), (gx - 5, gy - 5), 1)
        ground_band(76)
        return

    # ─── PRISM ──────────────────────────────────────────────────────────────
    # Prismatic: cycling-color crossing beams, crystal facet shapes,
    # prismatic halo rings from a central point, light-burst rays.
    if bg_kind == "prism":
        prism_cols = [haze, cloud, pipe, (200, 255, 200), (255, 200, 255), (200, 200, 255)]
        # Cycling-color crossing beam grid
        for i in range(18):
            x = (i * 60 + int(t * 24)) % WIDTH
            col = prism_cols[i % len(prism_cols)]
            pygame.draw.line(surf, col, (x, 0), (WIDTH - x, HEIGHT), 2)
            pygame.draw.line(surf, cloud, (WIDTH - x, 0), (x, HEIGHT), 1)
        # Crystal facet shapes
        for i in range(8):
            x = 54 + i * 118 + int(math.sin(t * 0.7 + i) * 16)
            pts = [(x, 34), (x + 30, 74), (x + 16, 130), (x - 22, 98)]
            pygame.draw.polygon(surf, cloud, pts, 1)
            pygame.draw.polygon(surf, pipe_dark,
                [(x + 6, 50), (x + 22, 76), (x + 10, 110), (x - 6, 88)], 1)
        # Prismatic halo rings from center
        for hi in range(4):
            cr = 220 + hi * 76
            hcol = prism_cols[(hi + 1) % len(prism_cols)]
            pygame.draw.circle(surf, hcol, (WIDTH // 2, HEIGHT // 3), cr, 1)
        # Light-burst radial rays
        for i in range(12):
            ang = i * (math.tau / 12) + t * 0.35
            ex = WIDTH // 2 + int(math.cos(ang) * 200)
            ey = HEIGHT // 3 + int(math.sin(ang) * 130)
            pygame.draw.line(surf, prism_cols[i % len(prism_cols)],
                (WIDTH // 2, HEIGHT // 3), (ex, ey), 1)
        ground_band(72)
        return

    # ─── BLOOM ──────────────────────────────────────────────────────────────
    # Organic garden: animated flowering vine stems, multi-branch leaves,
    # full flower crowns, drifting petals, swirling top-arc tendrils.
    if bg_kind == "bloom":
        # Main vine trunks with branching leaves and flower crowns
        for i in range(9):
            x = 52 + i * 106 + int(math.sin(t * 0.75 + i) * 10)
            stem_h = 86 + (i % 3) * 28
            pygame.draw.line(surf, pipe_dark,
                (x, HEIGHT - 76), (x + int(math.sin(t * 0.5 + i) * 12), HEIGHT - 76 - stem_h), 5)
            # Side leaf branches
            for lj in range(3):
                ly = HEIGHT - 76 - 18 - lj * 24
                ldx = 20 * (1 if lj % 2 == 0 else -1)
                pygame.draw.line(surf, pipe_dark, (x, ly), (x + ldx, ly - 14), 3)
                pygame.draw.ellipse(surf, cloud, (x + ldx - 12, ly - 20, 24, 14))
            # Flower crown
                fy = HEIGHT - 76 - stem_h - 20
            pygame.draw.ellipse(surf, cloud, (x - 28, fy - 20, 56, 40))
            pygame.draw.ellipse(surf, haze,  (x - 16, fy -  8, 32, 20))
            pygame.draw.circle(surf, pipe, (x, fy), 6)
        # Background diamond leaf shapes
        for i in range(6):
            lx = 84 + i * 152 + int(math.sin(t * 0.5 + i) * 14)
            ly = 52 + (i % 2) * 30
            pts = [(lx, ly + 20), (lx + 24, ly + 6), (lx + 48, ly + 22), (lx + 24, ly + 44)]
            pygame.draw.polygon(surf, pipe, pts)
            pygame.draw.polygon(surf, haze,
                [(lx + 10, ly + 18), (lx + 24, ly + 10), (lx + 38, ly + 22), (lx + 24, ly + 36)], 1)
        # Drifting petals
        for i in range(18):
            px = (i * 58 + int(t * 36)) % WIDTH
            py = (i * 47 + int(t * 26)) % (HEIGHT - 110) + 18
            plen = 7 + (i % 3) * 3
            pygame.draw.ellipse(surf, haze, (px, py, plen, max(1, plen // 2)))
        # Top arc vine curtains
        for i in range(5):
            pygame.draw.arc(surf, cloud,  (34 + i * 178, 26, 164, 98), 0.0, math.pi, 2)
            pygame.draw.arc(surf, pipe_dark, (56 + i * 178, 44, 118, 62), 0.1, math.pi - 0.1, 1)
        ground_band(74)
        return

    # ─── EMBER ──────────────────────────────────────────────────────────────
    # Infernal forge: tall volcano-pillars with lava cracks, floating ember
    # rain, diagonal heat-haze lines, lava-glow ground pools.
    if bg_kind == "ember":
        # Volcanic pillar towers
        for i in range(8):
            x = 38 + i * 124 + int(math.sin(t * 0.6 + i) * 16)
            pygame.draw.polygon(surf, pipe_dark,
                [(x, HEIGHT - 80), (x + 46, HEIGHT - 80), (x + 28, 86), (x - 8, 86)])
            # Lava crack down pillar
            pygame.draw.line(surf, haze, (x + 16, 88), (x + 10, HEIGHT - 84), 2)
            # Fire tips at pillar top
            for fk in range(3):
                fx_off = int(math.sin(t * 6.2 + i * 0.8 + fk) * 5)
                pygame.draw.line(surf, (255, 180, 60),
                    (x + 16 + fx_off, 86 + fk * 9), (x + 10 + fx_off, 70 + fk * 9), 2)
        # Ember crack arcs in the sky
        for i in range(9):
            cx2 = 66 + i * 110 + int(math.sin(t * 0.5 + i) * 12)
            cy2 = 52 + (i % 2) * 28 + int(math.sin(t * 1.2 + i) * 8)
            pygame.draw.line(surf, haze,  (cx2, cy2), (cx2 + 24, cy2 + 44), 2)
            pygame.draw.line(surf, cloud, (cx2 + 6, cy2 + 6), (cx2 + 16, cy2 + 30), 1)
        # Floating ember rain
        for i in range(28):
            x = (i * 44 + int(t * 48)) % (WIDTH + 100) - 50
            pygame.draw.circle(surf, cloud, (x, 22 + (i % 6) * 22), 2)
        # Diagonal heat-haze streaks
        for i in range(14):
            x = 54 + i * 70 + int(math.sin(t * 1.0 + i) * 10)
            pygame.draw.line(surf, haze, (x, 0), (x + 24, HEIGHT), 1)
        # Lava-glow ground
        pygame.draw.rect(surf, ground, (0, HEIGHT - 80, WIDTH, 80))
        for i in range(7):
            lx = 46 + i * 138
            pygame.draw.ellipse(surf, (196, 48, 8), (lx - 20, HEIGHT - 36, 40, 14))
            pygame.draw.ellipse(surf, (255, 110, 24), (lx - 8, HEIGHT - 30, 16, 8))
        pygame.draw.rect(surf, pipe_dark, (0, HEIGHT - 80, WIDTH, 10))
        # Ground spikes
        for i in range(14):
            x = i * 72 + int(math.sin(t * 1.0 + i) * 8)
            tip = 16 + int((math.sin(t * 2.2 + i * 0.5) + 1) * 9)
            pygame.draw.polygon(surf, pipe, [(x, HEIGHT - 80), (x + 22, HEIGHT - 80), (x + 11, HEIGHT - 80 - tip)])
        return

    # ─── TIDE ───────────────────────────────────────────────────────────────
    # Deep ocean: sweeping full-width wave bands, rising bubble curtain,
    # coral branch formations, glinting water-shimmer nodes.
    if bg_kind == "tide":
        # Full-width sweeping wave bands
        for i in range(12):
            y_base = 76 + i * 28 + int(math.sin(t * 1.0 + i * 0.4) * 7)
            pygame.draw.arc(surf, cloud, (-28, y_base, WIDTH + 56, 82), 0.0, math.pi, 4)
            pygame.draw.arc(surf, haze,  (-72, y_base + 14, WIDTH + 144, 52), 0.0, math.pi, 2)
        # Rising bubble curtain
        for i in range(22):
            bx = 40 + i * 44 + int(math.sin(t * 2.0 + i * 0.7) * 10)
            by = HEIGHT - 30 - int(((t * 50 + i * 58) % (HEIGHT - 62)))
            pygame.draw.circle(surf, pipe, (bx, by), 3, 1)
            pygame.draw.circle(surf, cloud, (bx + 1, by - 1), 1)
        # Coral branch formations at base
        for i in range(8):
            cx2 = 46 + i * 122 + int(math.sin(t * 0.5 + i) * 8)
            ch = 34 + (i % 3) * 18
            for j in range(3):
                bx2 = cx2 + (j - 1) * 16
                bh = ch - j * 10
                pygame.draw.line(surf, pipe_dark, (bx2, HEIGHT - 72),
                    (bx2 + int(math.sin(t * 1.1 + i + j) * 5), HEIGHT - 72 - bh), 5)
                pygame.draw.circle(surf, haze, (bx2 + int(math.sin(t * 1.1 + i + j) * 5), HEIGHT - 72 - bh), 6)
        # Water-shimmer glint nodes
        for i in range(16):
            wx = 52 + i * 58 + int(math.sin(t * 2.4 + i) * 12)
            wy = 144 + (i % 4) * 20 + int(math.sin(t * 3.0 + i) * 6)
            pygame.draw.circle(surf, pipe, (wx, wy), 4)
            pygame.draw.arc(surf, pipe_dark, (wx - 20, wy - 12, 40, 28), 0.0, math.pi, 2)
        ground_band(70)
        return

    # ─── FROST ──────────────────────────────────────────────────────────────
    # Arctic citadel: 6-pointed snowflake crystals with arms and branches,
    # blizzard streaks, tapering ice-pillar columns at base.
    if bg_kind == "frost":
        # Blizzard diagonal streaks
        for i in range(30):
            x = (i * 40 + int(t * 24)) % WIDTH
            y = 14 + (i * 27) % 200
            length = 20 + (i % 3) * 8
            pygame.draw.line(surf, haze,  (x, y), (x + length, y + 44), 1)
            pygame.draw.line(surf, cloud, (x + length, y + 44), (x + length // 2 - 6, y + 56), 1)
        # 6-pointed snowflake crystals
        for sf in range(9):
            sfx = 52 + sf * 106 + int(math.sin(t * 0.55 + sf) * 10)
            sfy = 40 + (sf % 2) * 28 + int(math.cos(t * 0.78 + sf) * 8)
            rsf = 14 + (sf % 3) * 4
            for arm in range(6):
                ang = arm * (math.pi / 3) + sf * 0.2
                ex = sfx + int(math.cos(ang) * rsf)
                ey = sfy + int(math.sin(ang) * rsf)
                pygame.draw.line(surf, haze, (sfx, sfy), (ex, ey), 2)
                # Two sub-branches per arm
                for br in range(2):
                    frac = 0.38 + br * 0.3
                    bx = sfx + int(math.cos(ang) * (rsf * frac))
                    by = sfy + int(math.sin(ang) * (rsf * frac))
                    pygame.draw.line(surf, cloud, (bx, by),
                        (bx + int(math.cos(ang + 0.95) * 5), by + int(math.sin(ang + 0.95) * 5)), 1)
                    pygame.draw.line(surf, cloud, (bx, by),
                        (bx + int(math.cos(ang - 0.95) * 5), by + int(math.sin(ang - 0.95) * 5)), 1)
            pygame.draw.circle(surf, cloud, (sfx, sfy), 2)
        # Ice pillar columns rising from ground
        for i in range(11):
            px = 40 + i * 88 + int(math.sin(t * 0.65 + i) * 6)
            ph = 64 + (i % 3) * 32 + int(math.sin(t * 0.4 + i) * 10)
            pts_ice = [(px, HEIGHT - 76), (px + 16, HEIGHT - 76),
                       (px + 12, HEIGHT - 76 - ph), (px + 4, HEIGHT - 76 - ph - 14)]
            pygame.draw.polygon(surf, cloud, pts_ice)
            pygame.draw.polygon(surf, pipe_dark, pts_ice, 1)
        ground_band(74)
        return

    # ─── STELLAR ────────────────────────────────────────────────────────────
    # Cosmic forge: dense star field, twinkling accent stars, constellation
    # line path, nebula arc wisps, pulsing nova burst ring, rocket shapes.
    if bg_kind == "stellar":
        # Dense star background
        for i in range(96):
            x = (i * 31 + int(t * 10)) % WIDTH
            y = (i * 49 + int(t * 7)) % (HEIGHT - 34) + 14
            pygame.draw.circle(surf, cloud, (x, y), 1)
        # Brighter twinkling accent stars
        for i in range(14):
            x = (i * 79 + int(t * 6)) % WIDTH
            y = (i * 61 + int(t * 4)) % (HEIGHT // 2) + 12
            pygame.draw.circle(surf, cloud, (x, y), 2)
            pygame.draw.line(surf, haze, (x - 6, y), (x + 6, y), 1)
            pygame.draw.line(surf, haze, (x, y - 6), (x, y + 6), 1)
        # Constellation line path
        star_pts = [(112, 42), (204, 66), (336, 36), (478, 70), (618, 48), (756, 40), (862, 66)]
        for i in range(len(star_pts) - 1):
            pygame.draw.line(surf, haze, star_pts[i], star_pts[i + 1], 1)
        for pt in star_pts:
            pygame.draw.circle(surf, cloud, pt, 2)
        # Nebula arc wisps
        for i in range(6):
            nx = 72 + i * 162 + int(math.sin(t * 0.4 + i) * 20)
            ny = 28 + (i % 2) * 38
            pygame.draw.arc(surf, haze,  (nx - 52, ny, 138, 82), 0.2, 5.7, 2)
            pygame.draw.arc(surf, cloud, (nx - 30, ny + 16, 88, 46), 0.3, 5.2, 1)
        # Pulsing nova burst ring
        nv_r = int(58 + 22 * math.sin(t * 1.6))
        pygame.draw.circle(surf, haze, (WIDTH // 2, 78), nv_r, 2)
        pygame.draw.circle(surf, pipe, (WIDTH // 2, 78), max(1, nv_r - 16), 1)
        for i in range(10):
            ang = t * 0.6 + i * (math.tau / 10)
            ox = WIDTH // 2 + int(math.cos(ang) * nv_r)
            oy = 78 + int(math.sin(ang) * nv_r * 0.72)
            pygame.draw.circle(surf, haze, (ox, oy), 3)
        # Rocket/triangle markers
        for i in range(5):
            x = 106 + i * 176 + int(math.sin(t * 0.5 + i) * 10)
            pygame.draw.polygon(surf, pipe_dark, [(x, 168), (x + 20, 216), (x - 20, 216)])
            pygame.draw.polygon(surf, haze, [(x, 182), (x + 8, 216), (x - 8, 216)], 1)
        ground_band(72)
        return

    # ─── OBSIDIAN ───────────────────────────────────────────────────────────
    # Dark crystal seraph: radiating fracture cracks from a central point,
    # obsidian spire formations at base, dark crystal pillars at top,
    # slow-moving crossing void lines.
    if bg_kind == "obsidian":
        # Radiating fracture cracks from upper-center
        ccx, ccy = WIDTH // 2, 96
        for i in range(16):
            ang = i * (math.pi / 8) + t * 0.05
            length = 110 + (i % 4) * 58
            ex = ccx + int(math.cos(ang) * length)
            ey = ccy + int(math.sin(ang) * length)
            pygame.draw.line(surf, haze, (ccx, ccy), (ex, ey), 1)
            # Sub-branch cracks
            mx = ccx + int(math.cos(ang) * length * 0.5)
            my = ccy + int(math.sin(ang) * length * 0.5)
            ba = ang + 0.52
            pygame.draw.line(surf, pipe_dark, (mx, my),
                (mx + int(math.cos(ba) * 44), my + int(math.sin(ba) * 44)), 1)
        # Dark crystal pillar formations at top
        for i in range(7):
            x = 74 + i * 134 + int(math.sin(t * 0.65 + i) * 10)
            sh = 80 + (i % 3) * 42 + int(math.sin(t * 0.4 + i) * 8)
            pts_p = [(x - 10, HEIGHT - 76), (x + 10, HEIGHT - 76),
                     (x + 14, HEIGHT - 76 - int(sh * 0.58)), (x, HEIGHT - 76 - sh),
                     (x - 14, HEIGHT - 76 - int(sh * 0.58))]
            pygame.draw.polygon(surf, pipe_dark, pts_p)
            pygame.draw.polygon(surf, cloud,
                [(x - 4, HEIGHT - 76), (x + 4, HEIGHT - 76),
                 (x + 6, HEIGHT - 76 - int(sh * 0.5)), (x, HEIGHT - 76 - int(sh * 0.9))], 1)
        # Floating dark crystal shapes at mid-screen
        for i in range(7):
            x = 76 + i * 132 + int(math.sin(t * 0.7 + i) * 10)
            pygame.draw.polygon(surf, pipe_dark, [(x, 44), (x + 36, 114), (x + 16, 192), (x - 22, 122)])
            pygame.draw.polygon(surf, cloud,    [(x + 8, 66), (x + 20, 98), (x + 8, 132), (x - 4, 100)], 1)
        # Slowly drifting crossing void lines
        for i in range(22):
            x = (i * 56 + int(t * 15)) % WIDTH
            pygame.draw.line(surf, haze, (x, 0), (WIDTH - x, HEIGHT), 1)
        ground_band(76)
        return

    # ─── NOVA ───────────────────────────────────────────────────────────────
    # Supernova crown: concentric expanding burst rings, dense radial rays,
    # two orbiting starlet belts, background star field, cosmic ray lines.
    if bg_kind == "nova":
        cn = (WIDTH // 2, 88)
        # Concentric burst rings (6 layers)
        for ri in range(6):
            rn = int(38 + ri * 58 + 18 * math.sin(t * 1.4 + ri))
            cn_col = pipe if ri % 2 == 0 else haze
            if rn > 0:
                pygame.draw.circle(surf, cn_col, cn, rn, 2 if ri < 4 else 1)
        # Dense radial rays
        for i in range(20):
            ang = t * 0.65 + i * (math.tau / 20)
            r_inner = 28
            r_outer = 94 + (i % 4) * 8
            x1 = cn[0] + int(math.cos(ang) * r_inner)
            y1 = cn[1] + int(math.sin(ang) * r_inner)
            x2 = cn[0] + int(math.cos(ang) * r_outer)
            y2 = cn[1] + int(math.sin(ang) * r_outer)
            pygame.draw.line(surf, haze, (x1, y1), (x2, y2), 2)
        # Orbiting starlet belts (two orbits)
        for orbit in (138, 192):
            for i in range(12):
                ang = t * 0.48 + i * (math.tau / 12)
                ox = cn[0] + int(math.cos(ang) * orbit)
                oy = cn[1] + int(math.sin(ang) * orbit * 0.54)
                pygame.draw.circle(surf, cloud, (ox, oy), 4)
                pygame.draw.circle(surf, pipe_dark, (ox, oy), 12, 1)
        # Background star field
        for i in range(48):
            x = (i * 27 + int(t * 7)) % WIDTH
            y = (i * 61 + int(t * 5)) % (HEIGHT - 40) + 14
            pygame.draw.circle(surf, cloud, (x, y), 1)
        # Cosmic ray diagonal lines
        for i in range(5):
            ang = 0.28 + i * 0.22 + t * 0.14
            x0 = int(cn[0] - math.cos(ang) * 560)
            y0 = int(cn[1] - math.sin(ang) * 560)
            x1 = int(cn[0] + math.cos(ang) * 560)
            y1 = int(cn[1] + math.sin(ang) * 560)
            pygame.draw.line(surf, pipe_dark, (x0, y0), (x1, y1), 1)
        ground_band(72)
        return

    # ─── RIFT ───────────────────────────────────────────────────────────────
    # Dimensional tear: warped perspective grid, vertical jagged rift tears,
    # portal arc vortexes, shifting diagonal rift streaks.
    if bg_kind == "rift":
        # Warped perspective grid
        for row in range(8):
            y = 18 + row * 58 + int(math.sin(t * 0.8 + row) * 6)
            prev_x = 0
            for col in range(15):
                x = col * 68 + int(math.sin(t * 1.2 + row + col * 0.32) * 9)
                if col > 0:
                    pygame.draw.line(surf, pipe_dark, (prev_x, y), (x, y), 1)
                prev_x = x
        # Vertical jagged rift tears (5 tears)
        for i in range(5):
            rx = 112 + i * 176 + int(math.sin(t * 0.5 + i) * 18)
            prev = (rx, 8)
            for seg in range(12):
                ny = prev[1] + 20 + (seg % 2) * 8
                nx = rx + int(math.sin(t * 3.6 + i * 1.5 + seg * 0.9) * 18)
                pygame.draw.line(surf, haze, prev, (nx, ny), 2)
                pygame.draw.line(surf, pipe_dark, (prev[0] - 1, prev[1]), (nx - 1, ny), 1)
                prev = (nx, ny)
                if ny > HEIGHT - 100:
                    break
        # Portal arc vortexes (4 portals)
        for i in range(4):
            x = 78 + i * 242 + int(math.sin(t * 1.1 + i) * 14)
            y = 52 + (i % 2) * 30
            pygame.draw.arc(surf, cloud,    (x - 48, y,      134, 80), 0.4, 5.2, 3)
            pygame.draw.arc(surf, pipe_dark, (x - 26, y + 10, 100, 48), 0.8, 4.8, 2)
        # Shifting diagonal rift streaks
        for i in range(24):
            x = (i * 50 + int(t * 30)) % WIDTH
            pygame.draw.line(surf, haze, (x, 0), (x - 30, HEIGHT), 1)
        ground_band(70)
        return

    # ─── THORN ──────────────────────────────────────────────────────────────
    # Thorn sovereign: dense thorn-vine columns with diamond thorns and
    # leaf crowns, sweeping top-arc curtains, drifting leaf particles.
    if bg_kind == "thorn":
        # Main thorn-vine columns
        for i in range(10):
            x = 48 + i * 96 + int(math.sin(t * 0.9 + i) * 10)
            pygame.draw.line(surf, pipe_dark, (x, HEIGHT - 72), (x, 84), 5)
            # Diamond thorns along vine
            for j in range(5):
                yy = 88 + j * 30 + int(math.sin(t * 1.9 + i + j) * 4)
                # Alternating left/right thorns
                for dx in (-16, 16):
                    pts_t = [(x, yy), (x + dx, yy + 5), (x, yy + 12), (x - dx // 2, yy + 5)]
                    pygame.draw.polygon(surf, haze, pts_t)
            # Leaf crown at top
            lx = x + int(math.sin(t * 0.7 + i) * 8)
            ly = 84
            pygame.draw.ellipse(surf, cloud, (lx - 26, ly - 32, 52, 32))
            pygame.draw.ellipse(surf, pipe,  (lx - 14, ly - 20, 28, 18))
        # Background arc vine curtains across top
        for i in range(6):
            pygame.draw.arc(surf, cloud,    (32 + i * 162, 24, 166, 100), 0.0, math.pi, 2)
            pygame.draw.arc(surf, pipe_dark, (54 + i * 162, 42, 122,  64), 0.08, math.pi - 0.08, 1)
        # Drifting falling leaves
        for i in range(18):
            lx = (i * 56 + int(t * 40)) % WIDTH
            ly = (i * 49 + int(t * 28)) % (HEIGHT - 110) + 18
            llen = 8 + (i % 3) * 3
            pygame.draw.ellipse(surf, haze, (lx, ly, llen, max(1, llen // 2)))
        ground_band(76)
        return

    # ─── SENTINEL ───────────────────────────────────────────────────────────
    # Rotating shield arrays, animated scan-beam sweep, tall sentinel
    # pillar pairs with pulsing nodes, drifting sensor dot field.
    if bg_kind == "sentinel":
        # Drifting sensor dot field
        for i in range(28):
            x = (i * 42 + int(t * 14)) % WIDTH
            y = 22 + (i * 35) % 190
            pygame.draw.circle(surf, cloud, (x, y), 2)
        # Animated horizontal scan-beam sweep
        scan_y = int((t * 64) % HEIGHT)
        for sw in range(-3, 4):
            sy = (scan_y + sw * 9) % HEIGHT
            al = max(0, 110 - abs(sw) * 28)
            scan_s = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
            scan_s.fill((*haze, al))
            surf.blit(scan_s, (0, sy))
        # Sentinel pillar towers with pulsing nodes
        for i in range(8):
            x = 70 + i * 112 + int(math.sin(t * 1.4 + i) * 8)
            pygame.draw.rect(surf, pipe_dark, (x, 36, 22, 136), border_radius=8)
            pygame.draw.rect(surf, haze,      (x - 7, 28, 36, 18), border_radius=8)
            # Pulsing light node
            pygame.draw.circle(surf, cloud, (x + 11, 36 + 68), 5)
            pygame.draw.circle(surf, haze,  (x + 11, 36 + 68), 9, 1)
        # Rotating shield arc arrays (3 stations)
        for sa_i in range(3):
            sa_cx = 196 + sa_i * 284
            sa_cy = 90
            for sa_r in range(3):
                rv = 26 + sa_r * 16
                sa_start = t * (0.85 + sa_i * 0.28 + sa_r * 0.12) + sa_i * 1.3
                pygame.draw.arc(surf, haze if sa_r == 0 else cloud,
                    (sa_cx - rv, sa_cy - rv, rv * 2, rv * 2),
                    sa_start, sa_start + 3.0, 2)
        ground_band(72)
        return

    # ─── AURORA (Aurora Heart — fallback) ───────────────────────────────────
    # Flowing multi-layer aurora ribbon curtains, twinkling star backdrop,
    # shimmering light pillar columns, arc ornament crown.
    # Star backdrop
    for i in range(32):
        x = (i * 37 + int(t * 8)) % WIDTH
        y = (i * 59 + int(t * 5)) % (HEIGHT // 2) + 10
        pygame.draw.circle(surf, cloud, (x, y), 1)
    # Multi-layer aurora ribbon curtains
    ribbon_colors = [haze, cloud, pipe, haze]
    for ci, col in enumerate(ribbon_colors):
        for x in range(0, WIDTH, 4):
            yy = HEIGHT // 3 + int(math.sin(x * 0.011 + t * (0.9 + ci * 0.3) + ci * 1.7) * (34 + ci * 10))
            pygame.draw.line(surf, col, (x, yy), (x, yy + 12 + ci * 6), 2)
    # Second deeper ribbon layer
    for x in range(0, WIDTH, 6):
        yy2 = int(HEIGHT * 0.52) + int(math.sin(x * 0.014 + t * 1.35) * 22)
        pygame.draw.line(surf, pipe_dark, (x, yy2), (x, yy2 + 22), 2)
    # Aurora arc crown ornaments
    for i in range(7):
        x = 54 + i * 138 + int(math.sin(t * 0.7 + i) * 20)
        pygame.draw.arc(surf, haze,  (x - 40, 14,  98, 264), 0.4, 2.6, 4)
        pygame.draw.arc(surf, cloud, (x - 12,  8, 130, 272), 0.2, 2.9, 2)
    # Light pillar columns
    for i in range(6):
        x = 98 + i * 152 + int(math.sin(t * 0.9 + i) * 14)
        pygame.draw.line(surf, pipe_dark, (x, 54), (x, HEIGHT - 70), 3)
        pygame.draw.circle(surf, pipe, (x, 174), 14)
        pygame.draw.circle(surf, haze, (x, 174), 7)
    ground_band(72)

def draw_boss_cinematic_fx(surf: pygame.Surface, theme: dict, bg_kind: str, boss, t: float):
    spec = boss.spec()
    accent = spec["accent"]
    core = spec["core"]
    dark = spec["dark"]
    phase = max(1, int(getattr(boss, "phase", 1)))
    progress = 0.0
    duration = max(0.001, float(getattr(boss, "phase_transition_duration", 0.0) or 0.0))
    if duration > 0.0:
        progress = clamp(float(getattr(boss, "phase_transition_timer", duration)) / duration, 0.0, 1.0)
    flash = 1.0 - ease_out_cubic(clamp(progress, 0.0, 1.0))
    intensity = 0.16 + 0.10 * (phase - 1) + 0.20 * flash

    fx = get_clear_surface((WIDTH, HEIGHT), ("boss_cinematic_fx", bg_kind))
    cx = WIDTH // 2
    cy = 118

    if bg_kind == "hell":
        for i in range(5):
            radius = int(58 + i * (38 + phase * 4) + flash * (54 + i * 14))
            alpha = int((92 - i * 12) * (0.55 + intensity))
            pygame.draw.circle(fx, (*accent, max(0, alpha)), (cx, cy), radius, 4 if i < 3 else 2)
        for i in range(18):
            ang = t * (0.95 + i * 0.02) + i * (math.tau / 18)
            length = 120 + phase * 20 + int(26 * flash)
            px = cx + int(math.cos(ang) * length)
            py = cy + int(math.sin(ang) * length * 0.72)
            pygame.draw.line(fx, (*core, 80 + int(80 * flash)), (cx, cy), (px, py), 2)
        for i in range(24):
            sx = (i * 43 + int(t * 80)) % WIDTH
            sy = 26 + (i % 6) * 16 + int(math.sin(t * 6.0 + i) * 5)
            pygame.draw.circle(fx, (*accent, 170), (sx, sy), 2)
        for i in range(10):
            x = 36 + i * 92 + int(math.sin(t * 2.4 + i) * 10)
            y = HEIGHT - 108 + int(math.sin(t * 4.8 + i) * 10)
            pygame.draw.polygon(fx, (*accent, 80 + int(60 * flash)), [(x, y), (x + 9, y - 12), (x + 16, y), (x + 8, y + 12)])
        for i in range(6):
            rx = 72 + i * 146 + int(math.sin(t * (1.1 + i * 0.04)) * 18)
            pygame.draw.arc(fx, (*dark, 120), (rx - 72, 34, 144, 220), 0.4, 2.7, 2)
            pygame.draw.arc(fx, (*core, 140), (rx - 56, 42, 112, 198), 0.2, 2.9, 1)
        return

    if bg_kind in {"void", "rift", "nova", "stellar", "obsidian"}:
        for i in range(4):
            radius = int(54 + i * (40 + phase * 4) + flash * (48 + i * 12))
            alpha = int((82 - i * 12) * (0.5 + intensity))
            pygame.draw.circle(fx, (*accent, max(0, alpha)), (cx, cy), radius, 3 if i < 3 else 2)
        for i in range(8):
            ang = t * (0.55 + i * 0.02) + i * (math.tau / 8)
            length = 138 + phase * 12 + int(22 * flash)
            px = cx + int(math.cos(ang) * length)
            py = cy + int(math.sin(ang) * length * 0.68)
            pygame.draw.line(fx, (*core, 90 + int(50 * flash)), (cx, cy), (px, py), 2)
    elif bg_kind in {"ember", "tide", "frost", "aegis"}:
        for i in range(5):
            rr = int(42 + i * (28 + phase * 3) + flash * 30)
            alpha = int((70 - i * 10) * (0.62 + intensity))
            pygame.draw.circle(fx, (*core, max(0, alpha)), (cx, cy), rr, 2 if i != 2 else 3)
        for i in range(6):
            y = 54 + i * 22 + int(math.sin(t * (1.5 + i * 0.15)) * (3 + phase))
            pygame.draw.line(fx, (*accent, 38 + int(28 * flash)), (0, y), (WIDTH, y), 1)
    else:
        for i in range(6):
            rr = int(36 + i * (24 + phase * 3) + flash * 34)
            pygame.draw.arc(fx, (*accent, 78), (cx - rr, cy - rr, rr * 2, rr * 2), 0.2 + t * 0.3, 3.0 + t * 0.3, 2)
        pygame.draw.circle(fx, (*core, 110), (cx, cy), int(34 + 18 * flash), 2)

    if phase >= 2:
        for i in range(10):
            ang = t * (1.2 + phase * 0.08) + i * (math.tau / 10)
            rr = 76 + phase * 10 + int(10 * math.sin(t * 2.0 + i))
            px = cx + int(math.cos(ang) * rr)
            py = cy + int(math.sin(ang) * rr * 0.70)
            pygame.draw.circle(fx, (*accent, 94 + int(60 * flash)), (px, py), 2)
    if phase >= 3:
        for i in range(5):
            ang = t * 2.3 + i * (math.tau / 5)
            x1 = cx + int(math.cos(ang) * 18)
            y1 = cy + int(math.sin(ang) * 18)
            x2 = cx + int(math.cos(ang) * (160 + 18 * i))
            y2 = cy + int(math.sin(ang) * (110 + 12 * i))
            pygame.draw.line(fx, (*core, 110), (x1, y1), (x2, y2), 1)

    vignette = get_clear_surface((WIDTH, HEIGHT), ("boss_cinematic_vignette", bg_kind))
    vignette.fill((0, 0, 0, 10 + int(14 * intensity)))
    pygame.draw.ellipse(vignette, (*dark, 0), pygame.Rect(-140, -70, WIDTH + 280, HEIGHT + 140))
    fx.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(fx, (0, 0))

def draw_boss_pipe_preview_label(surf: pygame.Surface, rect: pygame.Rect, title: str, subtitle: str, color: Tuple[int, int, int]):
    draw_round_rect(surf, (16, 20, 32), rect, radius=18)
    draw_round_rect(surf, color, rect, radius=18, width=2)
    draw_text(surf, get_cached_sysfont("arial", 16, bold=True), title, (rect.centerx, rect.y + 8), color, center=True, shadow=False)
    draw_text(surf, get_cached_sysfont("arial", 13), subtitle, (rect.centerx, rect.y + rect.height - 18), WHITE, center=True, shadow=False)

def boss_visual_center(boss) -> tuple[int, int]:
    bob = math.sin(boss.wobble * (2.0 + boss.boss_id * 0.12)) * (12 + boss.phase * 4 + boss.boss_id * 1.2)
    return int(boss.x), int(boss.y + bob)

def boss_visual_rotation(boss) -> float:
    return math.sin(boss.wobble * 2.3) * (2.4 + boss.phase * 0.4)

def draw_boss_body_surface(spec: dict, boss) -> tuple[pygame.Surface, pygame.Rect]:
    body = get_clear_surface((460, 300), ("boss_body", spec.get("short", spec.get("art", "aegis"))))
    main = spec["body"]
    accent = spec["accent"]
    dark = spec["dark"]
    core = spec["core"]
    boss_kind = spec.get("art", "aegis")
    is_hell = spec.get("short") == "HELL"
    t = boss.phase_timer
    pulse = 0.5 + 0.5 * math.sin(t * 2.1)
    glow = 0.5 + 0.5 * math.sin(t * 3.7 + boss.boss_id)
    rage = 1.0 + 0.2 * max(0, boss.phase - 1) + (0.15 if boss.enraged else 0.0)

    def sparkle(x, y, c=core, s=4):
        pygame.draw.circle(body, c, (int(x), int(y)), s)

    def line_arc(color, rect, start, end, width=2):
        pygame.draw.arc(body, color, rect, start, end, width)

    if boss_kind == "aegis":
        # A shield-engine that opens and closes in layers.
        center = (226, 130)
        shield_r = 70 + int(math.sin(t * 1.8) * 4)
        pygame.draw.circle(body, main, center, 92)
        pygame.draw.circle(body, dark, center, 66)
        pygame.draw.circle(body, core, center, 18)
        line_arc(accent, (center[0] - shield_r, center[1] - shield_r, shield_r * 2, shield_r * 2), t * 0.9, t * 0.9 + 4.8, 4)
        line_arc(core, (center[0] - 56, center[1] - 56, 112, 112), t * 1.4, t * 1.4 + 5.2, 2)
        for i in range(4):
            ang = t * 1.8 + i * (math.tau / 4)
            px = center[0] + int(math.cos(ang) * 102)
            py = center[1] + int(math.sin(ang) * 72)
            pygame.draw.polygon(body, accent, [(px, py - 10), (px + 8, py), (px, py + 10), (px - 8, py)])
            pygame.draw.circle(body, core, (px, py), 4)
        for x in (126, 186, 266, 326):
            pygame.draw.rect(body, accent, (x, 194, 12, 40), border_radius=4)
            pygame.draw.rect(body, core, (x + 2, 202, 8, 12), border_radius=2)
        sparkle(226, 130, accent, 7)

    elif boss_kind == "tempest":
        # A wind-borer with rotating storm blades.
        pivot = (230, 132)
        swing = 0.5 + 0.5 * math.sin(t * 2.8)
        pygame.draw.polygon(body, main, [(86, 98), (150, 54), (208, 76), (258, 46), (320, 70), (378, 120), (314, 172), (250, 154), (214, 186), (154, 162), (114, 178), (64, 132)])
        pygame.draw.polygon(body, dark, [(132, 104), (184, 74), (224, 92), (266, 74), (310, 106), (258, 144), (214, 138), (174, 154), (136, 136)])
        pygame.draw.circle(body, core, pivot, 16)
        for i in range(5):
            ang = t * (2.1 + 0.2 * i) + i * (math.tau / 5)
            px = pivot[0] + int(math.cos(ang) * (62 + i * 4))
            py = pivot[1] + int(math.sin(ang) * (42 + i * 3))
            pygame.draw.polygon(body, accent, [(px, py), (px + 24, py - 8), (px + 8, py + 16)])
            pygame.draw.line(body, core, pivot, (px, py), 2)
        for y in (64, 94, 124, 154, 184):
            pygame.draw.arc(body, accent, (76, y - 16, 260, 38), t * 0.7, t * 0.7 + 2.4 + swing, 2)
        line_arc(core, (88, 54, 248, 140), 0.15 + t * 0.3, 2.7 + t * 0.3, 2)

    elif boss_kind == "void":
        # A black-hole shrine with orbiting shards.
        center = (226, 130)
        pygame.draw.circle(body, dark, center, 94)
        pygame.draw.circle(body, main, center, 94, 3)
        pygame.draw.circle(body, core, center, 22)
        for orbit in (42, 66, 92):
            line_arc(accent, (center[0] - orbit, center[1] - orbit, orbit * 2, orbit * 2), t * (0.9 + orbit / 120), t * (0.9 + orbit / 120) + 5.0, 2)
        for i in range(7):
            ang = t * 0.9 + i * (math.tau / 7)
            px = center[0] + int(math.cos(ang) * (100 + (i % 2) * 10))
            py = center[1] + int(math.sin(ang) * (72 + (i % 3) * 6))
            pts = [(px, py - 14), (px + 10, py), (px, py + 14), (px - 10, py)]
            pygame.draw.polygon(body, accent, pts)
            pygame.draw.circle(body, core, (px, py), 3)
        for y in (52, 86, 168, 202):
            pygame.draw.arc(body, (*accent, 120), (96, y - 8, 240, 20), 0.0, math.pi, 2)

    elif boss_kind == "chrono":
        # A living clockwork fortress.
        center = (226, 130)
        pygame.draw.circle(body, main, center, 88)
        pygame.draw.circle(body, dark, center, 60)
        pygame.draw.circle(body, core, center, 16)
        for i in range(12):
            ang = i * (math.tau / 12)
            px = center[0] + int(math.cos(ang) * 92)
            py = center[1] + int(math.sin(ang) * 92)
            pygame.draw.line(body, accent, center, (px, py), 2)
            pygame.draw.circle(body, accent, (px, py), 4)
        for ring in (38, 58, 80):
            line_arc(core if ring == 38 else accent, (center[0] - ring, center[1] - ring, ring * 2, ring * 2), t * 0.8, t * 0.8 + 5.1, 2)
        hour = t * 0.45
        minute = t * 1.4
        pygame.draw.line(body, core, center, (center[0] + int(math.cos(hour) * 28), center[1] + int(math.sin(hour) * 28)), 4)
        pygame.draw.line(body, accent, center, (center[0] + int(math.cos(minute) * 44), center[1] + int(math.sin(minute) * 44)), 2)
        for x in (122, 170, 214, 258, 306):
            pygame.draw.rect(body, accent, (x, 38, 12, 18), border_radius=2)
            pygame.draw.rect(body, accent, (x, 204, 12, 18), border_radius=2)

    elif boss_kind == "prism":
        # Faceted crystal prism that splits into moving shards.
        center = (226, 126)
        scale = 1.0 + 0.03 * math.sin(t * 2.4)
        pts = [(center[0], 26), (294, 86), (268, 186), (184, 208), (132, 142), (152, 64)]
        pygame.draw.polygon(body, main, pts)
        pygame.draw.polygon(body, dark, [(226, 46), (272, 92), (252, 164), (192, 182), (158, 134), (170, 78)])
        pygame.draw.polygon(body, core, [(226, 66), (246, 96), (234, 136), (214, 142), (198, 112), (206, 78)])
        for i in range(6):
            ang = t * (0.7 + 0.1 * i) + i * (math.tau / 6)
            px = center[0] + int(math.cos(ang) * (90 + i * 2))
            py = center[1] + int(math.sin(ang) * (58 + i))
            pygame.draw.line(body, accent, center, (px, py), 2)
            pygame.draw.polygon(body, accent, [(px, py - 10), (px + 8, py), (px, py + 10), (px - 8, py)])
        for x in (120, 170, 218, 266, 316):
            pygame.draw.line(body, core, (x, 44), (x - 8, 196), 1)
        sparkle(226, 126, core, 6)

    elif boss_kind == "bloom":
        # A flowering vine-heart that opens like a breathing blossom.
        open_amt = 0.45 + 0.35 * (math.sin(t * 1.8) + 1) * 0.5
        center = (226, 130)
        pygame.draw.circle(body, main, center, 72)
        pygame.draw.circle(body, dark, center, 46)
        pygame.draw.circle(body, core, center, 16)
        for i in range(10):
            ang = i * (math.tau / 10) + t * 0.18
            rad = 68 + int(math.sin(t * 2.0 + i) * 5)
            px = center[0] + int(math.cos(ang) * rad)
            py = center[1] + int(math.sin(ang) * rad * 0.72)
            petal = [(px, py - int(18 * open_amt)), (px + 12, py), (px, py + int(18 * open_amt)), (px - 12, py)]
            pygame.draw.polygon(body, accent, petal)
        for y in (66, 98, 162, 194):
            pygame.draw.arc(body, (*core, 160), (92, y - 8, 268, 24), 0.0, math.pi, 2)
        pygame.draw.line(body, accent, (172, 218), (160, 256), 3)
        pygame.draw.line(body, accent, (278, 218), (292, 256), 3)
        pygame.draw.circle(body, core, (150, 244), 4)
        pygame.draw.circle(body, core, (304, 244), 4)

    elif boss_kind == "ember":
        # A furnace-warlord with glowing fractures and ash sparks.
        center = (226, 132)
        pulse2 = 0.65 + 0.35 * math.sin(t * 3.0)
        pygame.draw.polygon(body, main, [(98, 94), (150, 42), (288, 42), (342, 94), (314, 198), (146, 198)])
        pygame.draw.polygon(body, dark, [(148, 92), (176, 68), (280, 68), (306, 94), (286, 174), (160, 174)])
        pygame.draw.polygon(body, core, [(200, 104), (226, 78), (252, 104), (238, 136), (212, 136)])
        for x in range(126, 334, 20):
            pygame.draw.line(body, accent, (x, 54), (x - 20 + int(math.sin(t * 5.0 + x * 0.07) * 5), 192), 1)
        for i in range(14):
            px = 120 + i * 20 + int(math.sin(t * 7.0 + i) * 2)
            py = 28 + int((math.sin(t * 2.6 + i * 0.8) + 1) * 18)
            pygame.draw.circle(body, accent, (px, py), 2)
        pygame.draw.arc(body, (*core, 160), (128, 76, 200, 96), 0.1, 3.0, 2)
        pygame.draw.arc(body, (*accent, 200), (152, 100, 152, 72), 0.0, 3.1, 2)
        if is_hell:
            crown_pts = [(132, 54), (166, 24), (196, 52), (226, 18), (256, 52), (286, 24), (320, 54), (304, 86), (226, 92), (148, 86)]
            pygame.draw.polygon(body, (92, 10, 10), crown_pts)
            pygame.draw.polygon(body, accent, crown_pts, 2)
            pygame.draw.circle(body, (255, 248, 220), (226, 130), 22)
            pygame.draw.circle(body, (255, 166, 78), (226, 130), 42, 2)
            for x in range(116, 336, 18):
                wob = int(math.sin(t * 7.5 + x * 0.12) * 6)
                pygame.draw.line(body, (255, 120, 54), (x, 42), (x - 16 + wob, 196), 2)
                pygame.draw.line(body, (70, 10, 10), (x + 2, 48), (x - 4 + wob, 192), 1)
            for i in range(18):
                ang = t * 3.2 + i * (math.tau / 18)
                rr = 82 + int(6 * math.sin(t * 4.0 + i))
                px = center[0] + int(math.cos(ang) * rr)
                py = center[1] + int(math.sin(ang) * rr * 0.72)
                pygame.draw.circle(body, (255, 180, 90, 170), (px, py), 2)
            if boss.phase >= 2:
                for i in range(6):
                    yy = 72 + i * 22 + int(math.sin(t * 4.2 + i) * 5)
                    pygame.draw.arc(body, (255, 150, 64, 150), (104, yy - 6, 244, 22), 0.0, math.pi, 2)
            if boss.phase >= 3:
                for i in range(6):
                    ang = t * 2.6 + i * (math.tau / 6)
                    px = center[0] + int(math.cos(ang) * (104 + i * 3))
                    py = center[1] + int(math.sin(ang) * (76 + i * 2))
                    pygame.draw.line(body, (255, 236, 196, 170), center, (px, py), 2)

    elif boss_kind == "tide":
        # A marine oracle with flowing fins and wave bands.
        center = (226, 132)
        wave = 0.5 + 0.5 * math.sin(t * 2.2)
        pygame.draw.circle(body, main, center, 74)
        pygame.draw.circle(body, dark, center, 50)
        pygame.draw.circle(body, core, center, 16)
        for i in range(8):
            x = 116 + i * 36
            y = 88 + int(math.sin(t * 2.6 + i) * 10)
            pygame.draw.arc(body, accent, (x - 24, y - 12, 48, 26), 0.0, math.pi, 2)
        for i in range(4):
            ang = t * 0.9 + i * (math.tau / 4)
            px = center[0] + int(math.cos(ang) * (82 + i * 4))
            py = center[1] + int(math.sin(ang) * (40 + i * 3))
            pygame.draw.ellipse(body, accent, (px - 10, py - 18, 20, 36))
        pygame.draw.arc(body, core, (120, 44, 220, 148), 0.1 + wave * 0.2, 2.9 + wave * 0.2, 3)
        pygame.draw.arc(body, (*accent, 170), (136, 60, 188, 116), 0.2, 2.7, 2)

    elif boss_kind == "frost":
        # An ice citadel with snow caps and crystal spikes.
        center = (226, 130)
        frost_pulse = 0.5 + 0.5 * math.sin(t * 2.4)
        pygame.draw.polygon(body, main, [(226, 22), (302, 78), (286, 188), (166, 188), (150, 78)])
        pygame.draw.polygon(body, dark, [(226, 48), (272, 88), (260, 154), (192, 154), (180, 88)])
        pygame.draw.polygon(body, core, [(226, 68), (248, 96), (238, 132), (214, 132), (204, 96)])
        pygame.draw.rect(body, (*core, 120), (136, 32, 180, 20), border_radius=8)
        for x in range(118, 340, 18):
            spike = 8 + int((math.sin(t * 3.2 + x * 0.1) + 1) * 4)
            pygame.draw.polygon(body, accent, [(x, 186), (x - 6, 186 - spike), (x + 6, 186 - spike)])
        for i in range(6):
            sx = 140 + i * 40 + int(math.sin(t * 1.5 + i) * 4)
            sy = 220 + int(math.sin(t * 2.0 + i) * 3)
            pygame.draw.circle(body, core, (sx, sy), 3)
        sparkle(226, 130, core, 6)

    elif boss_kind == "stellar":
        # A cosmic forge with orbiting planets and flaring rays.
        center = (226, 126)
        pygame.draw.polygon(body, main, [(226, 26), (288, 74), (268, 166), (226, 212), (184, 166), (164, 74)])
        pygame.draw.polygon(body, dark, [(226, 52), (264, 86), (252, 150), (226, 176), (200, 150), (188, 86)])
        pygame.draw.circle(body, core, center, 18)
        for i in range(6):
            ang = t * (0.7 + 0.15 * i) + i * (math.tau / 6)
            px = center[0] + int(math.cos(ang) * (70 + i * 7))
            py = center[1] + int(math.sin(ang) * (54 + i * 4))
            pygame.draw.circle(body, accent, (px, py), 5)
            pygame.draw.line(body, accent, center, (px, py), 2)
        for i in range(10):
            ang = i * (math.tau / 10) + t * 1.2
            px = center[0] + int(math.cos(ang) * 96)
            py = center[1] + int(math.sin(ang) * 72)
            pygame.draw.line(body, core, center, (px, py), 2)
        line_arc(accent, (120, 44, 200, 164), t * 0.5, t * 0.5 + 5.5, 2)

    elif boss_kind == "obsidian":
        # A dark seraph blade with cutting shard wings.
        center = (226, 130)
        flutter = 0.5 + 0.5 * math.sin(t * 3.0)
        pygame.draw.polygon(body, main, [(226, 20), (300, 82), (280, 186), (172, 186), (152, 82)])
        pygame.draw.polygon(body, dark, [(226, 46), (272, 86), (258, 148), (194, 148), (180, 86)])
        pygame.draw.polygon(body, core, [(226, 66), (246, 92), (236, 128), (216, 128), (206, 92)])
        for i in range(6):
            ang = t * 0.8 + i * (math.tau / 6)
            px = center[0] + int(math.cos(ang) * (90 + i * 2))
            py = center[1] + int(math.sin(ang) * (58 + i * 3))
            pts = [(px, py - 14), (px + 12, py), (px, py + 14), (px - 12, py)]
            pygame.draw.polygon(body, accent, pts)
        pygame.draw.line(body, core, (116, 58), (344, 206), 2)
        pygame.draw.line(body, accent, (344, 58), (116, 206), 2)
        pygame.draw.arc(body, (*accent, 120), (122, 40, 208, 166), 0.2, 2.6, 2)

    elif boss_kind == "nova":
        center = (226, 128)
        pygame.draw.circle(body, main, center, 82)
        pygame.draw.circle(body, dark, center, 54)
        pygame.draw.circle(body, core, center, 16)
        for i in range(10):
            ang = t * 1.5 + i * (math.tau / 10)
            px = center[0] + int(math.cos(ang) * (72 + (i % 2) * 10))
            py = center[1] + int(math.sin(ang) * (54 + (i % 3) * 4))
            pygame.draw.line(body, accent, center, (px, py), 2)
            pygame.draw.circle(body, accent, (px, py), 4)
        for i in range(4):
            ang = t * (2.0 + i * 0.2) + i * (math.tau / 4)
            px = center[0] + int(math.cos(ang) * 102)
            py = center[1] + int(math.sin(ang) * 72)
            pygame.draw.polygon(body, core, [(px, py - 8), (px + 10, py), (px, py + 8), (px - 10, py)])
        pygame.draw.arc(body, (*accent, 200), (128, 48, 196, 132), t * 0.4, t * 0.4 + 3.8, 2)

    elif boss_kind == "rift":
        center = (226, 130)
        pygame.draw.circle(body, dark, center, 90)
        pygame.draw.circle(body, accent, center, 90, 3)
        for i in range(9):
            ang = t * 1.2 + i * (math.tau / 9)
            px = center[0] + int(math.cos(ang) * (64 + i * 2))
            py = center[1] + int(math.sin(ang) * (44 + i * 2))
            pygame.draw.line(body, accent, center, (px, py), 2)
            pygame.draw.polygon(body, core, [(px, py - 10), (px + 8, py), (px, py + 10), (px - 8, py)])
        pygame.draw.arc(body, (*core, 180), (128, 54, 196, 140), 0.2, 5.7, 2)
        pygame.draw.polygon(body, main, [(120, 84), (160, 46), (206, 74), (252, 44), (326, 96), (274, 156), (198, 136), (164, 176), (118, 144)])

    elif boss_kind == "thorn":
        center = (226, 130)
        pygame.draw.circle(body, main, center, 82)
        pygame.draw.circle(body, dark, center, 56)
        pygame.draw.circle(body, core, center, 16)
        for i in range(10):
            ang = i * (math.tau / 10) + t * 0.16
            px = center[0] + int(math.cos(ang) * 82)
            py = center[1] + int(math.sin(ang) * 60)
            petal = [(px, py - 14), (px + 10, py), (px, py + 14), (px - 10, py)]
            pygame.draw.polygon(body, accent, petal)
        for i in range(5):
            x = 124 + i * 58
            pygame.draw.line(body, accent, (x, 74), (x + 18, 190), 2)
            pygame.draw.polygon(body, core, [(x + 10, 98), (x + 18, 108), (x + 8, 114), (x, 104)])
        pygame.draw.arc(body, (*core, 180), (108, 46, 240, 150), 0.3, 2.8, 2)

    elif boss_kind == "sentinel":
        center = (226, 130)
        pygame.draw.polygon(body, main, [(226, 18), (300, 74), (282, 188), (170, 188), (152, 74)])
        pygame.draw.polygon(body, dark, [(226, 44), (270, 84), (258, 152), (194, 152), (182, 84)])
        pygame.draw.polygon(body, core, [(226, 64), (248, 92), (236, 132), (216, 132), (204, 92)])
        for i in range(8):
            ang = t * (0.8 + i * 0.02) + i * (math.tau / 8)
            px = center[0] + int(math.cos(ang) * (92 + (i % 2) * 5))
            py = center[1] + int(math.sin(ang) * (64 + (i % 3) * 5))
            pygame.draw.rect(body, accent, (px - 6, py - 6, 12, 12), border_radius=3)
            pygame.draw.line(body, accent, center, (px, py), 2)
        pygame.draw.arc(body, (*accent, 200), (118, 42, 224, 168), t * 0.2, t * 0.2 + 5.0, 2)

    else:  # aurora
        # A light-ribbon heart with drifting bands.
        center = (226, 128)
        pulse3 = 0.5 + 0.5 * math.sin(t * 2.8)
        pygame.draw.circle(body, main, center, 76)
        pygame.draw.circle(body, dark, center, 52)
        pygame.draw.circle(body, core, center, 16)
        for i in range(6):
            ang = t * (0.8 + 0.08 * i) + i * (math.tau / 6)
            r = 72 + int(math.sin(t * 2.0 + i) * 5)
            px = center[0] + int(math.cos(ang) * r)
            py = center[1] + int(math.sin(ang) * 48)
            pygame.draw.arc(body, accent, (px - 20, py - 12, 40, 24), 0.0, math.pi, 2)
        for y in range(50, 190, 16):
            offset = int(math.sin(t * 2.2 + y * 0.09) * 8)
            pygame.draw.arc(body, (*core, 170), (92 + offset, y - 6, 276, 18), 0.0, math.pi, 2)
        for i in range(4):
            px = 142 + i * 56 + int(math.sin(t * 1.6 + i) * 4)
            pygame.draw.circle(body, accent, (px, 214), 4)
            pygame.draw.line(body, accent, (px, 214), (px, 248), 2)

    # A much stronger phase ramp so later phases feel visibly more dangerous.
    phase_boost = 1.0 + 0.06 * max(0, boss.phase - 1) + (0.06 if boss.enraged else 0.0)
    if boss.phase >= 2:
        for i in range(5):
            ox = 58 + i * 96 + int(math.sin(t * 3.0 + i) * 12)
            oy = 34 + int(math.sin(t * 2.1 + i) * 10)
            pygame.draw.circle(body, (*accent, 88), (ox, oy), 4 + (i % 2))
            pygame.draw.circle(body, (*core, 140), (ox + 18, oy + 10), 2)
        for i in range(4):
            xx = 94 + i * 74 + int(math.sin(t * 4.4 + i) * 8)
            pygame.draw.line(body, (*core, 120), (xx, 14), (xx - 10, 274), 2)
    if boss.phase >= 3:
        for i in range(10):
            ang = t * (2.6 + i * 0.02) + i * (math.tau / 10)
            px = 226 + int(math.cos(ang) * 132)
            py = 126 + int(math.sin(ang) * 96)
            pygame.draw.circle(body, (*accent, 95), (px, py), 3)
        pygame.draw.circle(body, (*core, 110), (226, 126), 108, 2)

    if is_hell:
        for i in range(28):
            ang = t * (3.6 + i * 0.04) + i * (math.tau / 28)
            rr = 102 + int(10 * math.sin(t * 5.0 + i)) + (i % 4) * 4
            px = 226 + int(math.cos(ang) * rr)
            py = 130 + int(math.sin(ang) * rr * 0.70)
            pygame.draw.circle(body, (255, 170, 92, 100), (px, py), 2)
        for i in range(5):
            y = 50 + i * 38 + int(math.sin(t * 5.0 + i) * 7)
            pygame.draw.arc(body, (255, 140, 60, 130), (96, y - 12, 268, 28), 0.0, math.pi, 2)
        if boss.phase >= 2:
            for i in range(8):
                ang = t * 4.1 + i * (math.tau / 8)
                rr = 150 + int(10 * math.sin(t * 3.6 + i))
                px = 226 + int(math.cos(ang) * rr)
                py = 132 + int(math.sin(ang) * rr * 0.64)
                pygame.draw.circle(body, (255, 190, 110, 120), (px, py), 2)
                pygame.draw.line(body, (255, 132, 64, 140), (226, 132), (px, py), 1)
        if boss.phase >= 3:
            flame_pts = [(132, 54), (154, 20), (182, 58), (204, 16), (226, 50), (248, 16), (272, 58), (300, 20), (322, 54), (304, 94), (226, 104), (148, 94)]
            pygame.draw.polygon(body, (96, 8, 8), flame_pts)
            pygame.draw.polygon(body, (255, 118, 50), flame_pts, 2)
            for i in range(10):
                yy = 74 + i * 14 + int(math.sin(t * 8.0 + i) * 3)
                pygame.draw.arc(body, (255, 170, 84, 150), (100, yy - 4, 260, 14), 0.0, math.pi, 2)
            for i in range(8):
                ang = t * 5.3 + i * (math.tau / 8)
                rr = 132 + i * 3
                px = center[0] + int(math.cos(ang) * rr)
                py = center[1] + int(math.sin(ang) * rr * 0.70)
                pygame.draw.circle(body, (255, 232, 190, 150), (px, py), 3)

    rot = boss_visual_rotation(boss)
    scale = 1.0 + 0.03 * max(0, boss.phase - 1) + (0.04 if boss.enraged else 0.0) + (0.04 if boss.phase_changed else 0.0)
    if is_hell:
        scale += 0.03 * max(0, boss.phase - 1)
    img = pygame.transform.rotozoom(body, rot, scale)
    rect = img.get_rect(center=boss_visual_center(boss))
    return img, rect

def draw_boss_hitbox_surface(spec: dict, boss) -> tuple[pygame.Surface, pygame.Rect]:
    hitbox = get_clear_surface((460, 300), ("boss_hitbox", spec.get("short", spec.get("art", "aegis"))))
    solid = (255, 255, 255, 255)
    boss_kind = spec.get("art", "aegis")
    is_hell = spec.get("short") == "HELL"

    def poly(points):
        pygame.draw.polygon(hitbox, solid, points)

    def circle(center, radius):
        pygame.draw.circle(hitbox, solid, center, radius)

    def ellipse(rect):
        pygame.draw.ellipse(hitbox, solid, rect)

    if boss_kind == "aegis":
        circle((226, 130), 64)
    elif boss_kind == "tempest":
        poly([(136, 106), (184, 78), (224, 92), (264, 76), (306, 106), (260, 142), (214, 140), (176, 154), (140, 136)])
    elif boss_kind == "void":
        circle((226, 130), 70)
    elif boss_kind == "chrono":
        circle((226, 130), 68)
    elif boss_kind == "prism":
        poly([(226, 50), (266, 92), (252, 164), (194, 180), (160, 132), (174, 80)])
    elif boss_kind == "bloom":
        ellipse((164, 84, 124, 94))
    elif boss_kind == "ember":
        if is_hell:
            poly([(150, 96), (176, 70), (276, 70), (302, 96), (286, 178), (164, 178)])
        else:
            poly([(150, 96), (176, 70), (276, 70), (302, 96), (286, 174), (164, 174)])
    elif boss_kind == "tide":
        ellipse((160, 80, 132, 106))
    elif boss_kind == "frost":
        poly([(226, 50), (270, 88), (258, 158), (194, 158), (182, 88)])
    elif boss_kind == "stellar":
        poly([(226, 50), (264, 84), (252, 154), (226, 180), (200, 154), (188, 84)])
    elif boss_kind == "obsidian":
        poly([(226, 46), (272, 86), (258, 148), (194, 148), (180, 86)])
    elif boss_kind == "nova":
        circle((226, 128), 66)
    elif boss_kind == "rift":
        poly([(138, 90), (168, 60), (206, 82), (244, 60), (298, 98), (268, 150), (200, 136), (170, 164), (140, 138)])
    elif boss_kind == "thorn":
        ellipse((166, 84, 120, 96))
    elif boss_kind == "sentinel":
        poly([(226, 40), (272, 82), (258, 156), (194, 156), (180, 82)])
    else:  # aurora
        ellipse((164, 82, 124, 96))

    img = pygame.transform.rotozoom(hitbox, boss_visual_rotation(boss), 1.0)
    rect = img.get_rect(center=boss_visual_center(boss))
    return img, rect

def draw_mask_outline(surf: pygame.Surface, mask: pygame.mask.Mask, topleft: tuple[int, int], color, width: int = 2):
    outline = mask.outline()
    if len(outline) >= 2:
        points = [(topleft[0] + x, topleft[1] + y) for x, y in outline]
        pygame.draw.lines(surf, color, True, points, width)
        return
    for bounds in mask.get_bounding_rects():
        draw_round_outline(surf, color, bounds.move(topleft[0], topleft[1]), radius=16, width=width)

@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    size: float
    color: Tuple[int, int, int]
    gravity: float = 0.0

    def update(self, dt: float):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt

    def draw(self, surf: pygame.Surface):
        if self.life <= 0:
            return
        alpha = clamp(self.life / 0.7, 0.0, 1.0)
        radius = max(1, int(self.size * (0.6 + 0.8 * alpha)))
        overlay = get_particle_surface(radius, self.color, int(255 * alpha))
        surf.blit(overlay, (self.x - radius * 2, self.y - radius * 2))

@dataclass(slots=True)
class FloatingText:
    text: str
    x: float
    y: float
    vy: float
    life: float
    color: Tuple[int, int, int]

    def update(self, dt: float):
        self.life -= dt
        self.y += self.vy * dt

    def draw(self, surf, font):
        if self.life <= 0:
            return
        alpha = clamp(self.life / 1.0, 0.0, 1.0)
        img = render_text_cached(font, self.text, self.color).copy()
        img.set_alpha(int(255 * alpha))
        surf.blit(img, img.get_rect(center=(self.x, self.y)))

@dataclass(slots=True)
class Bird:
    x: float
    y: float
    vy: float = 0.0
    radius: int = 18
    skin_index: int = 0
    invuln: float = 0.0
    shield: float = 0.0
    boost: float = 0.0
    revives: int = 0
    wing_phase: float = 0.0

    def skin(self) -> Skin:
        return SKINS[self.skin_index]

    def flap(self, strength: float):
        self.vy = strength
        self.boost = 0.08

    def update(self, dt: float, difficulty: Difficulty, gravity_scale: float = 1.0):
        self.vy += difficulty.gravity * gravity_scale * dt
        self.y += self.vy * dt
        self.invuln = max(0.0, self.invuln - dt)
        self.shield = max(0.0, self.shield - dt)
        self.boost = max(0.0, self.boost - dt)
        self.wing_phase += dt * 14.0 + abs(self.vy) * 0.004

    def rect(self) -> pygame.Rect:
        # Slightly smaller and nudged toward the visible body center.
        # This keeps the hitbox inside the bird's oval shape and removes the
        # subtle right-side bias from the previous version.
        width = max(13, int(self.radius * 0.92))
        height = max(12, int(self.radius * 0.86))
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (int(round(self.x - 2)), int(round(self.y - 1)))
        return rect

    def draw(self, surf: pygame.Surface):
        skin = self.skin()
        angle = clamp(-self.vy * 0.06, -28, 34)
        r = self.radius
        cx = cy = r * 2
        flap = 0.5 + 0.5 * math.sin(self.wing_phase * 2.0)
        wing_raise = 1 if math.sin(self.wing_phase) > 0 else -1
        body = get_clear_surface((r * 4, r * 4), ("bird_draw", skin.name, r))
        body.blit(get_bird_body_surface(skin, r), (0, 0))

        wing_pts = [
            (cx - 2, cy + 1),
            (cx - int(15 + 5 * flap), cy - int(9 * wing_raise) - int(4 * flap)),
            (cx + int(4 - 2 * flap), cy - int(2 + 6 * flap)),
            (cx + int(7 + 2 * flap), cy + 3),
        ]
        pygame.draw.polygon(body, skin.bird_alt, wing_pts)

        img = fast_rotate_surface(body, angle)
        rect = img.get_rect(center=(self.x, self.y))
        surf.blit(img, rect)

        if self.shield > 0:
            shield_fx = get_clear_surface((r * 10, r * 10), ("bird_shield_fx", skin.name, r))
            pulse = 0.5 + 0.5 * math.sin(self.shield * 16.0)
            ring_r = int(r * (2.00 + 0.10 * pulse))
            core_r = int(r * (1.48 + 0.05 * pulse))
            cx2 = cy2 = r * 5
            shield_color = (*skin.accent, int(110 + 55 * pulse))
            inner_color = (180, 245, 255, int(45 + 45 * pulse))
            spark_color = (230, 250, 255, int(120 + 70 * pulse))

            pygame.draw.circle(shield_fx, (*skin.accent, int(18 + 18 * pulse)), (cx2, cy2), int(r * 2.65))
            pygame.draw.circle(shield_fx, shield_color, (cx2, cy2), ring_r, 4)
            pygame.draw.circle(shield_fx, inner_color, (cx2, cy2), core_r, 2)
            pygame.draw.circle(shield_fx, (255, 245, 200, int(22 + 16 * pulse)), (cx2, cy2), int(r * 0.92), 1)

            for i in range(6):
                ang = self.wing_phase * 0.9 + i * (math.tau / 6)
                px = cx2 + int(math.cos(ang) * (ring_r + 4))
                py = cy2 + int(math.sin(ang) * (ring_r + 4))
                pygame.draw.polygon(
                    shield_fx,
                    spark_color,
                    [(px, py - 4), (px + 3, py), (px, py + 4), (px - 3, py)],
                )

            for ang in BIRD_SHIELD_ARMS:
                px = cx2 + int(math.cos(ang + self.shield * 0.9) * (ring_r + 9))
                py = cy2 + int(math.sin(ang + self.shield * 0.9) * (ring_r + 9))
                pygame.draw.line(shield_fx, (*skin.accent, int(18 + 22 * pulse)), (cx2, cy2), (px, py), 1)

            surf.blit(shield_fx, shield_fx.get_rect(center=(self.x, self.y)))

        if self.invuln > 0:
            inv = get_clear_surface((r * 10, r * 10), ("bird_inv_fx", skin.name, r))
            pulse = 0.5 + 0.5 * math.sin(self.invuln * 14.0)
            cx2 = cy2 = r * 5
            outer_alpha = int(70 + 45 * pulse)
            halo_alpha = int(28 + 24 * pulse)
            ring_alpha = int(105 + 55 * pulse)

            pygame.draw.circle(inv, (*skin.accent, outer_alpha), (cx2, cy2), int(r * 3.0), 2)
            pygame.draw.circle(inv, (255, 235, 170, halo_alpha), (cx2, cy2), int(r * 2.05), 2)
            pygame.draw.circle(inv, (180, 245, 255, halo_alpha), (cx2, cy2), int(r * 1.32), 1)
            pygame.draw.circle(inv, (255, 245, 200, int(20 + 10 * pulse)), (cx2, cy2), int(r * 0.88), 1)

            for i in range(8):
                ang = self.wing_phase * 1.1 + i * (math.tau / 8)
                px = cx2 + int(math.cos(ang) * (r * 2.7))
                py = cy2 + int(math.sin(ang) * (r * 2.7))
                pygame.draw.circle(inv, (*skin.accent, ring_alpha), (px, py), 2)

            surf.blit(inv, inv.get_rect(center=(self.x, self.y)))

@dataclass(slots=True)
class Pipe:
    x: float
    gap_y: float
    gap_size: int
    width: int = 84
    scored: bool = False
    variant: int = 0
    move_phase: float = 0.0
    move_amp: float = 0.0
    speed: float = 250.0
    theme_index: int = 0

    def update(self, dt: float, difficulty: Difficulty, score: int):
        self.x -= self.speed * dt
        self.move_phase += dt * (0.9 + 0.1 * self.variant)

        if self.variant == 1:
            self.gap_y += math.sin(self.move_phase * 2.2) * self.move_amp * dt * 40
        elif self.variant == 2:
            self.gap_y += math.cos(self.move_phase * 1.8) * self.move_amp * dt * 32

        top_limit = 115
        bottom_limit = HEIGHT - 92
        self.gap_y = clamp(self.gap_y, top_limit + self.gap_size * 0.5, bottom_limit - self.gap_size * 0.5)

    def colliders(self) -> Tuple[pygame.Rect, pygame.Rect]:
        # Smaller pipe hitboxes for fairer collisions while keeping the same visuals.
        # Narrower width + extra padding near the gap reduces "cheap" hits.
        width = max(0, int(self.width * 0.76))
        x = int(round(self.x + (self.width - width) * 0.5))
        gap_margin = 14

        gap_top = max(0, int(round(self.gap_y - self.gap_size * 0.5)))
        gap_bottom = int(round(self.gap_y + self.gap_size * 0.5))

        top_h = max(0, gap_top - gap_margin)
        bot_y = gap_bottom + gap_margin
        bot_h = max(0, HEIGHT - bot_y)

        top_rect = pygame.Rect(x, 0, width, top_h)
        bot_rect = pygame.Rect(x, bot_y, width, bot_h)
        return top_rect, bot_rect

    def gap_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.gap_y - self.gap_size * 0.5), self.width, self.gap_size)

    def draw(self, surf: pygame.Surface, theme: dict, pulse: float = 0.0, boss_spec: Optional[dict] = None, boss_phase: int = 1, boss_timer: float = 0.0):
        top_rect, bot_rect = self.colliders()
        top_color = theme["pipe"]
        dark = theme["pipe_dark"]
        highlight_color = rgb_lerp(top_color, WHITE, 0.30)
        sheen_color = rgb_lerp(top_color, WHITE, 0.14)
        glow_color = rgb_lerp(theme["haze"], WHITE, 0.12)

        def draw_pipe_part(rect: pygame.Rect, flip: bool):
            if rect.height <= 0:
                return
            pygame.draw.rect(surf, dark, rect, border_radius=14)
            inner = rect.inflate(-10, -8)
            pygame.draw.rect(surf, top_color, inner, border_radius=12)
            lip_h = 18
            if flip:
                lip = pygame.Rect(rect.x - 6, rect.bottom - lip_h, rect.width + 12, lip_h)
            else:
                lip = pygame.Rect(rect.x - 6, rect.y, rect.width + 12, lip_h)
            pygame.draw.rect(surf, dark, lip, border_radius=10)
            lip2 = lip.inflate(-8, -6)
            pygame.draw.rect(surf, top_color, lip2, border_radius=8)

            # The original effect used an alpha surface here. Drawing the sheen
            # directly keeps the look while avoiding a per-height cache churn.
            pygame.draw.rect(surf, highlight_color, (rect.x + 6, rect.y + 8, 10, max(8, rect.height - 16)), border_radius=5)
            pygame.draw.line(surf, sheen_color, (rect.x + 18, rect.y + 10), (rect.x + 18, rect.bottom - 10), 1)

            if boss_spec is not None:
                boss_kind = boss_spec.get("art", "aegis")
                boss_short = boss_spec.get("short", "")
                accent = boss_spec["accent"]
                core = boss_spec["core"]
                body = boss_spec["body"]
                w = rect.width
                h = rect.height
                phase = boss_phase
                tt = boss_timer
                cx = rect.x + w // 2
                cy = rect.y + h // 2

                # Each boss gets a distinct silhouette treatment while keeping the arcade frame.
                if boss_kind == "aegis":
                    pygame.draw.polygon(surf, rgb_lerp(accent, WHITE, 0.08), [(cx, rect.y + 8), (cx + 16, rect.y + 18), (cx + 10, rect.y + 34), (cx - 10, rect.y + 34), (cx - 16, rect.y + 18)])
                    pygame.draw.polygon(surf, rgb_lerp(core, WHITE, 0.08), [(cx, rect.bottom - 10), (cx + 12, rect.bottom - 26), (cx, rect.bottom - 38), (cx - 12, rect.bottom - 26)])
                    for y in range(rect.y + 24, rect.bottom - 18, 28):
                        pygame.draw.line(surf, rgb_lerp(body, WHITE, 0.10), (rect.x + 8, y), (rect.right - 8, y), 1)
                    pygame.draw.arc(surf, rgb_lerp(accent, WHITE, 0.05), (rect.x + 10, rect.y + 18, w - 20, h - 36), 0.2 + tt * 0.8, 2.8 + tt * 0.8, 2)
                elif boss_kind == "tempest":
                    for y in range(rect.y + 14, rect.bottom - 10, 18):
                        offset = int(math.sin(tt * 4.0 + y * 0.1) * 5)
                        pygame.draw.polygon(surf, rgb_lerp(accent, WHITE, 0.04), [(rect.x + 8, y), (rect.right - 8, y - 6 + offset), (rect.right - 8, y + 8 + offset), (rect.x + 8, y + 14)])
                    pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.07), (rect.x + 10, rect.y + 18), (rect.right - 10, rect.bottom - 24), 2)
                    pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.07), (rect.right - 18, rect.y + 18), (rect.x + 18, rect.bottom - 24), 2)
                elif boss_kind == "void":
                    for y in range(rect.y + 18, rect.bottom - 14, 22):
                        pygame.draw.arc(surf, rgb_lerp(accent, WHITE, 0.05), (rect.x + 4, y - 10, w - 8, 20), tt * 1.2, tt * 1.2 + 2.8, 2)
                    pygame.draw.circle(surf, rgb_lerp(body, WHITE, 0.08), (cx, cy), max(10, min(w, h) // 4), 2)
                    pygame.draw.circle(surf, rgb_lerp(core, WHITE, 0.10), (cx, cy), 5)
                elif boss_kind == "chrono":
                    for y in range(rect.y + 10, rect.bottom - 8, 18):
                        pygame.draw.line(surf, rgb_lerp(accent, WHITE, 0.06), (rect.x + 8, y), (rect.right - 8, y), 1)
                    dial_x = cx + int(math.sin(tt * 1.6) * 4)
                    pygame.draw.circle(surf, rgb_lerp(core, WHITE, 0.10), (dial_x, cy), 8, 2)
                    ang = tt * (1.2 + 0.08 * phase)
                    pygame.draw.line(surf, rgb_lerp(body, WHITE, 0.08), (dial_x, cy), (dial_x + int(math.cos(ang) * 16), cy + int(math.sin(ang) * 16)), 2)
                elif boss_kind == "prism":
                    for x in range(rect.x + 12, rect.right - 10, 20):
                        pts = [(x, rect.y + 8), (x + 8, rect.y + 18), (x, rect.y + 30), (x - 8, rect.y + 18)]
                        pygame.draw.polygon(surf, rgb_lerp(accent, WHITE, 0.07), pts)
                    pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.08), (rect.x + 8, rect.bottom - 10), (rect.right - 8, rect.y + 10), 1)
                    pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.08), (rect.x + 8, rect.y + 10), (rect.right - 8, rect.bottom - 10), 1)
                elif boss_kind == "bloom":
                    for x in range(rect.x + 10, rect.right - 10, 18):
                        leaf_y = rect.y + 14 + int((math.sin(tt * 2.4 + x * 0.07) + 1) * 7)
                        pygame.draw.ellipse(surf, rgb_lerp(accent, WHITE, 0.06), (x - 4, leaf_y, 8, 16))
                    pygame.draw.arc(surf, rgb_lerp(core, WHITE, 0.08), (rect.x + 8, rect.y + 6, w - 16, h - 12), 0.2, 2.9, 2)
                elif boss_kind == "ember":
                    if boss_short == "HELL":
                        for x in range(rect.x + 8, rect.right - 8, 12):
                            crack = 10 + int((math.sin(tt * 7.0 + x * 0.18) + 1) * 5)
                            pygame.draw.line(surf, (255, 128, 62), (x, rect.y + 8), (x - crack // 2, rect.bottom - 8), 2)
                            pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.04), (x + 2, rect.y + 14), (x + 2, rect.bottom - 14), 1)
                        for y in range(rect.y + 10, rect.bottom - 8, 16):
                            flame = 6 + int((math.sin(tt * 4.2 + y * 0.12) + 1) * 5)
                            pygame.draw.polygon(surf, (255, 110, 42), [(rect.x + 8, y), (rect.right - 8, y - flame), (rect.right - 8, y + 8), (rect.x + 8, y + 14)])
                        for i in range(6):
                            px = cx + int(math.sin(tt * 5.5 + i) * (w * 0.18))
                            py = cy + int(math.cos(tt * 4.5 + i) * (h * 0.12))
                            pygame.draw.circle(surf, rgb_lerp(core, WHITE, 0.12), (px, py), 2)
                    else:
                        for x in range(rect.x + 10, rect.right - 10, 16):
                            crack = 12 + int((math.sin(tt * 6.0 + x * 0.15) + 1) * 4)
                            pygame.draw.line(surf, rgb_lerp(accent, WHITE, 0.05), (x, rect.y + 8), (x - crack // 2, rect.bottom - 8), 1)
                            pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.04), (x + 4, rect.y + 14), (x + 2, rect.bottom - 14), 1)
                elif boss_kind == "tide":
                    for y in range(rect.y + 12, rect.bottom - 8, 16):
                        pygame.draw.arc(surf, rgb_lerp(accent, WHITE, 0.06), (rect.x + 4, y - 6, w - 8, 16), 0.0, math.pi, 2)
                        pygame.draw.arc(surf, rgb_lerp(core, WHITE, 0.05), (rect.x + 10, y - 2, w - 20, 10), 0.0, math.pi, 1)
                elif boss_kind == "frost":
                    cap = pygame.Rect(rect.x + 6, rect.y + 6, w - 12, 16)
                    pygame.draw.rect(surf, rgb_lerp(core, WHITE, 0.08), cap, border_radius=7)
                    for x in range(rect.x + 10, rect.right - 10, 18):
                        tip = 6 + int((math.sin(tt * 3.2 + x * 0.12) + 1) * 4)
                        pygame.draw.polygon(surf, rgb_lerp(accent, WHITE, 0.06), [(x, rect.bottom - 8), (x - 6, rect.bottom - 8 - tip), (x + 6, rect.bottom - 8 - tip)])
                    for i in range(4):
                        sx = rect.x + 10 + i * (w - 20) / 3
                        pygame.draw.circle(surf, rgb_lerp(core, WHITE, 0.08), (int(sx), cy), 2)
                elif boss_kind == "stellar":
                    for i in range(4):
                        ang = tt * 0.9 + i * (math.tau / 4)
                        px = cx + int(math.cos(ang) * (18 + i * 3))
                        py = cy + int(math.sin(ang) * (10 + i * 2))
                        pygame.draw.circle(surf, rgb_lerp(accent, WHITE, 0.08), (px, py), 4)
                    pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.08), (rect.x + 8, cy), (rect.right - 8, cy), 2)
                    pygame.draw.line(surf, rgb_lerp(body, WHITE, 0.05), (cx, rect.y + 8), (cx, rect.bottom - 8), 2)
                elif boss_kind == "obsidian":
                    for x in range(rect.x + 8, rect.right - 8, 16):
                        hx = x + int(math.sin(tt * 2.5 + x * 0.2) * 3)
                        pygame.draw.polygon(surf, rgb_lerp(body, WHITE, 0.05), [(hx, rect.y + 8), (hx + 8, rect.y + 20), (hx + 2, rect.bottom - 8), (hx - 8, rect.y + 20)])
                    pygame.draw.line(surf, rgb_lerp(accent, WHITE, 0.05), (rect.x + 8, rect.bottom - 14), (rect.right - 8, rect.y + 14), 2)
                else:  # aurora
                    for y in range(rect.y + 8, rect.bottom - 8, 10):
                        offset = int(math.sin(tt * 2.0 + y * 0.08) * 6)
                        pygame.draw.arc(surf, rgb_lerp(accent, WHITE, 0.05), (rect.x + 4 + offset, y - 6, w - 8, 16), 0.0, math.pi, 2)
                    pygame.draw.arc(surf, rgb_lerp(core, WHITE, 0.08), (rect.x + 10, rect.y + 8, w - 20, h - 16), 0.1 + tt * 0.3, 2.9 + tt * 0.3, 2)

                for i in range(phase):
                    yy = rect.y + 18 + i * max(8, h // max(2, phase + 1))
                    pygame.draw.line(surf, rgb_lerp(accent, WHITE, 0.12), (rect.x + 8, yy), (rect.right - 8, yy + int(math.sin(tt * (2.3 + i * 0.5)) * 4)), 2)
                if phase >= 2:
                    for i in range(3):
                        ang = tt * 2.6 + i * (math.tau / 3)
                        x1 = rect.x + w * 0.5 + int(math.cos(ang) * 14)
                        y1 = rect.y + h * 0.5 + int(math.sin(ang) * 8)
                        x2 = rect.x + w * 0.5 + int(math.cos(ang) * (w * 0.42))
                        y2 = rect.y + h * 0.5 + int(math.sin(ang) * (h * 0.34))
                        pygame.draw.line(surf, rgb_lerp(core, WHITE, 0.06), (x1, y1), (x2, y2), 1)
                if phase >= 3:
                    for i in range(6):
                        x0 = rect.x + 12 + i * (w - 24) // 6
                        pygame.draw.circle(surf, rgb_lerp(core, WHITE, 0.08), (x0, rect.y + 14 + (i % 2) * (h - 28)), 2)

        draw_pipe_part(top_rect, False)
        draw_pipe_part(bot_rect, True)

        if self.variant > 0:
            # Small glow at the gap. Direct drawing is cheaper than creating a
            # separate alpha surface every frame.
            gap_top = int(self.gap_y - self.gap_size * 0.5) + 12
            gap_h = max(12, self.gap_size - 24)
            pygame.draw.rect(surf, glow_color, (self.x - 5, gap_top, self.width + 10, gap_h), border_radius=18)

@dataclass(slots=True)
class Orb:
    x: float
    y: float
    kind: str
    vx: float = -250.0
    active: bool = True
    phase: float = 0.0

    def update(self, dt: float):
        self.phase += dt * 5.0
        self.x += self.vx * dt

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - 15), int(self.y - 15), 30, 30)

    def draw(self, surf: pygame.Surface, skin: Skin):
        if not self.active:
            return

        pulse = 0.5 + 0.5 * math.sin(self.phase * 2.0)
        bob = math.sin(self.phase * 2.4) * 4.0
        sway = math.cos(self.phase * 1.7) * 3.0
        rot = self.phase * 90.0
        x = self.x + sway * 0.4
        y = self.y + bob

        color_map = {
            "shield": (100, 230, 255),
            "coin": (255, 220, 100),
            "magnet": (255, 120, 120),
            "boost": (160, 255, 180),
            "multiplier": (255, 175, 255),
            "revive": (255, 210, 120),
            "core": (255, 150, 90),
        }
        color = color_map.get(self.kind, skin.accent)

        phase_bucket = int((self.phase % math.tau) / math.tau * ORB_PHASE_BUCKETS)
        outer = get_orb_body_surface(self.kind, color, phase_bucket)
        img = fast_rotate_surface(outer, rot)
        rect = img.get_rect(center=(int(x), int(y)))
        surf.blit(img, rect)

@dataclass(slots=True)
class BossProjectile:
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    kind: str = "orb"
    boss_id: int = 0
    spin: float = 0.0
    age: float = 0.0

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.spin += dt * 10.0
        self.age += dt

    def rect(self) -> pygame.Rect:
        diameter = max(8, self.radius * 2)
        return pygame.Rect(int(self.x - diameter / 2), int(self.y - diameter / 2), diameter, diameter)

    def draw(self, surf: pygame.Surface):
        idx = self.boss_id % len(BOSS_SPECS)
        spec = BOSS_SPECS[idx]
        style = spec.get("projectile", spec.get("attack", "aegis"))
        accent = spec["accent"]
        core = spec["core"]
        dark = spec["dark"]
        body = spec["body"]
        is_hell = spec.get("short") == "HELL"
        age = float(getattr(self, "age", 0.0))
        intro = clamp(age / 0.24, 0.0, 1.0)
        intro_s = ease_out_cubic(intro)
        pulse = 0.82 + 0.18 * math.sin(self.spin * 0.8 + age * 8.0)
        size = self.radius * 8 + 24
        glow = get_clear_surface((size, size), ("boss_projectile_glow", style, self.radius, idx))
        cx = cy = size // 2
        trail = get_clear_surface((size, size), ("boss_projectile_trail", style, self.radius, idx))
        dirx = -1 if self.vx >= 0 else 1
        diry = -1 if self.vy >= 0 else 1
        trail_len = int((1.0 - intro_s) * (18 + self.radius * 1.9))
        if trail_len > 0:
            for i in range(4):
                t = i / 3.0
                px = cx + int(dirx * trail_len * (0.28 + t * 0.18))
                py = cy + int(diry * trail_len * (0.10 + t * 0.06))
                alpha = int(88 * (1.0 - t) * (1.0 - intro_s))
                pygame.draw.line(trail, (*accent, alpha), (px, py), (px - dirx * (12 + i * 2), py + i - 1), 2)
                pygame.draw.circle(trail, (*core, int(60 * (1.0 - t) * (1.0 - intro_s))), (px, py), max(1, 3 - i))
        if intro_s < 1.0:
            burst_r = int(self.radius * (2.9 - 1.5 * intro_s))
            pygame.draw.circle(trail, (*accent, int(180 * (1.0 - intro_s))), (cx, cy), burst_r, 2)
            pygame.draw.circle(trail, (*core, int(220 * (1.0 - intro_s))), (cx, cy), max(2, int(self.radius * (0.8 + 0.8 * intro_s))))
            for i in range(6):
                ang = self.spin * 0.9 + i * (math.tau / 6)
                px = cx + int(math.cos(ang) * (burst_r + 8))
                py = cy + int(math.sin(ang) * (burst_r + 8) * 0.72)
                pygame.draw.circle(trail, (*accent, int(120 * (1.0 - intro_s))), (px, py), 2)
        glow.blit(trail, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        if style == "aegis":
            pygame.draw.circle(glow, (*accent, 52), (cx, cy), self.radius * 2)
            pygame.draw.circle(glow, (*core, 220), (cx, cy), self.radius)
            pygame.draw.circle(glow, (*body, 220), (cx, cy), self.radius + 3, 3)
            pygame.draw.polygon(glow, (*accent, 230), [(cx, cy - 13), (cx + 10, cy), (cx, cy + 13), (cx - 10, cy)])
            pygame.draw.line(glow, (*body, 220), (cx - 13, cy), (cx + 13, cy), 2)
            pygame.draw.line(glow, (*body, 220), (cx, cy - 13), (cx, cy + 13), 2)
        elif style == "tempest":
            pygame.draw.circle(glow, (*accent, 62), (cx, cy), self.radius * 2)
            pts = [(cx - 14, cy - 2), (cx - 1, cy - 16), (cx + 12, cy - 3), (cx + 4, cy + 4), (cx + 17, cy + 16), (cx - 7, cy + 7)]
            pygame.draw.polygon(glow, (*body, 240), pts)
            pygame.draw.polygon(glow, (*core, 220), [(cx - 6, cy - 8), (cx + 5, cy - 1), (cx + 1, cy + 7), (cx - 8, cy + 2)])
            pygame.draw.arc(glow, (*accent, 220), (cx - self.radius * 2 + 4, cy - self.radius * 2 + 4, self.radius * 4 - 8, self.radius * 4 - 8), 0.3 + self.spin * 0.15, 4.1 + self.spin * 0.15, 3)
        elif style == "void":
            pygame.draw.circle(glow, (*accent, 48), (cx, cy), self.radius * 2)
            pygame.draw.circle(glow, (*dark, 230), (cx, cy), self.radius + 6)
            pygame.draw.circle(glow, (*core, 160), (cx + 6, cy - 2), max(2, self.radius // 2), 2)
            pygame.draw.arc(glow, (*accent, 220), (cx - self.radius * 2 + 4, cy - self.radius * 2 + 4, self.radius * 4 - 8, self.radius * 4 - 8), 0.2 + self.spin * 0.18, 3.9 + self.spin * 0.18, 3)
        elif style == "chrono":
            pygame.draw.circle(glow, (*accent, 58), (cx, cy), self.radius * 2)
            pygame.draw.circle(glow, (*body, 230), (cx, cy), self.radius + 1)
            pygame.draw.circle(glow, (*core, 220), (cx, cy), max(3, self.radius // 2))
            for a in range(8):
                ang = self.spin * 0.35 + a * (math.tau / 8)
                px = cx + int(math.cos(ang) * (self.radius + 7))
                py = cy + int(math.sin(ang) * (self.radius + 7))
                pygame.draw.line(glow, (*accent, 220), (cx, cy), (px, py), 2)
        elif style == "prism":
            pygame.draw.circle(glow, (*accent, 55), (cx, cy), self.radius * 2)
            pygame.draw.polygon(glow, (*body, 230), [(cx, cy - 18), (cx + 14, cy - 2), (cx + 6, cy + 14), (cx - 8, cy + 6), (cx - 14, cy - 5)])
            pygame.draw.polygon(glow, (*core, 240), [(cx, cy - 10), (cx + 9, cy), (cx + 4, cy + 8), (cx - 6, cy + 3), (cx - 9, cy - 3)])
            pygame.draw.arc(glow, (*accent, 220), (cx - self.radius * 2 + 5, cy - self.radius * 2 + 5, self.radius * 4 - 10, self.radius * 4 - 10), 0.8, 5.4, 2)
        elif style == "bloom":
            pygame.draw.circle(glow, (*accent, 50), (cx, cy), self.radius * 2)
            for ang in (0, math.pi * 0.5, math.pi, math.pi * 1.5):
                px = cx + int(math.cos(ang) * (self.radius + 8))
                py = cy + int(math.sin(ang) * (self.radius + 8))
                pygame.draw.ellipse(glow, (*body, 230), (px - 7, py - 12, 14, 24))
            pygame.draw.circle(glow, (*core, 230), (cx, cy), max(3, self.radius // 2))
        elif style == "ember":
            pygame.draw.circle(glow, (*accent, 60), (cx, cy), self.radius * 2)
            if is_hell:
                pts = [
                    (cx - 6, cy - 18), (cx + 6, cy - 14), (cx + 16, cy - 2),
                    (cx + 10, cy + 8), (cx + 18, cy + 18), (cx + 2, cy + 12),
                    (cx - 8, cy + 20), (cx - 16, cy + 4),
                ]
                pygame.draw.polygon(glow, (*body, 240), pts)
                pygame.draw.polygon(glow, (*dark, 180), [(cx - 1, cy - 10), (cx + 8, cy - 2), (cx + 2, cy + 7), (cx - 7, cy + 1)])
                for a in range(6):
                    ang = self.spin * 0.55 + a * (math.tau / 6)
                    px = cx + int(math.cos(ang) * (self.radius + 6))
                    py = cy + int(math.sin(ang) * (self.radius + 6) * 0.74)
                    pygame.draw.line(glow, (*accent, 120), (cx, cy), (px, py), 1)
            else:
                pygame.draw.polygon(glow, (*body, 240), [(cx - 3, cy - 16), (cx + 10, cy - 1), (cx + 1, cy + 7), (cx + 14, cy + 18), (cx - 8, cy + 8), (cx - 1, cy - 1)])
            pygame.draw.circle(glow, (*core, 230), (cx, cy), max(3, self.radius // 2))
        elif style == "tide":
            pygame.draw.circle(glow, (*accent, 58), (cx, cy), self.radius * 2)
            pygame.draw.arc(glow, (*body, 230), (cx - self.radius * 2 + 4, cy - self.radius * 2 + 8, self.radius * 4 - 8, self.radius * 4 - 10), 0.2, 3.0, 4)
            pygame.draw.arc(glow, (*core, 220), (cx - self.radius * 2 + 10, cy - self.radius * 2 + 14, self.radius * 4 - 20, self.radius * 4 - 22), 0.5, 2.6, 2)
            pygame.draw.circle(glow, (*core, 230), (cx, cy + 1), max(3, self.radius // 2))
        elif style == "frost":
            pygame.draw.circle(glow, (*accent, 48), (cx, cy), self.radius * 2)
            pygame.draw.polygon(glow, (*body, 235), [(cx, cy - 18), (cx + 12, cy - 2), (cx + 4, cy + 16), (cx - 8, cy + 4)])
            pygame.draw.polygon(glow, (*core, 240), [(cx, cy - 10), (cx + 7, cy), (cx + 3, cy + 7), (cx - 4, cy + 2)])
            pygame.draw.line(glow, (*accent, 220), (cx - 14, cy + 10), (cx + 14, cy - 10), 2)
        elif style == "stellar":
            pygame.draw.circle(glow, (*accent, 52), (cx, cy), self.radius * 2)
            pygame.draw.polygon(glow, (*body, 230), [(cx, cy - 16), (cx + 7, cy - 4), (cx + 18, cy), (cx + 7, cy + 4), (cx, cy + 16), (cx - 7, cy + 4), (cx - 18, cy), (cx - 7, cy - 4)])
            pygame.draw.circle(glow, (*core, 220), (cx, cy), max(3, self.radius // 2))
        elif style == "obsidian":
            pygame.draw.circle(glow, (*accent, 44), (cx, cy), self.radius * 2)
            pygame.draw.polygon(glow, (*dark, 230), [(cx - 2, cy - 16), (cx + 14, cy - 6), (cx + 7, cy + 12), (cx - 10, cy + 6), (cx - 14, cy - 2)])
            pygame.draw.polygon(glow, (*core, 220), [(cx + 1, cy - 9), (cx + 8, cy - 2), (cx + 3, cy + 7), (cx - 4, cy + 2)])
        elif style == "nova":
            pygame.draw.circle(glow, (*accent, 50), (cx, cy), self.radius * 2)
            for a in range(8):
                ang = self.spin * 0.42 + a * (math.tau / 8)
                px = cx + int(math.cos(ang) * (self.radius + 7))
                py = cy + int(math.sin(ang) * (self.radius + 7))
                pygame.draw.line(glow, (*core, 210), (cx, cy), (px, py), 2)
            pygame.draw.circle(glow, (*core, 230), (cx, cy), max(3, self.radius // 2))
        elif style == "rift":
            pygame.draw.circle(glow, (*accent, 40), (cx, cy), self.radius * 2)
            pygame.draw.arc(glow, (*accent, 220), (cx - self.radius * 2 + 4, cy - self.radius * 2 + 4, self.radius * 4 - 8, self.radius * 4 - 8), 0.6 + self.spin * 0.16, 4.9 + self.spin * 0.16, 3)
            pygame.draw.polygon(glow, (*dark, 230), [(cx - 12, cy), (cx, cy - 16), (cx + 12, cy), (cx, cy + 16)])
            pygame.draw.circle(glow, (*core, 210), (cx + 3, cy - 2), max(2, self.radius // 3))
        elif style == "thorn":
            pygame.draw.circle(glow, (*accent, 42), (cx, cy), self.radius * 2)
            pygame.draw.polygon(glow, (*body, 235), [(cx - 3, cy - 16), (cx + 12, cy - 2), (cx + 2, cy + 8), (cx + 14, cy + 18), (cx - 8, cy + 6), (cx - 1, cy - 1)])
            pygame.draw.line(glow, (*core, 220), (cx - 14, cy - 10), (cx + 14, cy + 10), 2)
            pygame.draw.circle(glow, (*core, 220), (cx, cy), max(3, self.radius // 2))
        elif style == "sentinel":
            pygame.draw.circle(glow, (*accent, 52), (cx, cy), self.radius * 2)
            pygame.draw.polygon(glow, (*body, 230), [(cx, cy - 18), (cx + 14, cy - 4), (cx + 8, cy + 16), (cx - 8, cy + 16), (cx - 14, cy - 4)])
            pygame.draw.polygon(glow, (*core, 240), [(cx, cy - 10), (cx + 7, cy), (cx, cy + 9), (cx - 7, cy)])
            pygame.draw.line(glow, (*accent, 210), (cx - 14, cy), (cx + 14, cy), 2)
        else:  # aurora
            pygame.draw.circle(glow, (*accent, 54), (cx, cy), self.radius * 2)
            pygame.draw.arc(glow, (*body, 230), (cx - self.radius * 2 + 4, cy - self.radius * 2 + 4, self.radius * 4 - 8, self.radius * 4 - 8), 0.7, 5.5, 2)
            pygame.draw.arc(glow, (*core, 220), (cx - self.radius * 2 + 10, cy - self.radius * 2 + 10, self.radius * 4 - 20, self.radius * 4 - 20), 1.0, 5.0, 2)
            pygame.draw.circle(glow, (*core, 230), (cx, cy), max(3, self.radius // 2))

        if intro_s < 1.0:
            entry = get_clear_surface((size, size), ("boss_projectile_entry", style, self.radius, idx))
            entry_r = int(self.radius * (2.2 - 0.95 * intro_s))
            pygame.draw.circle(entry, (*accent, int(160 * (1.0 - intro_s))), (cx, cy), entry_r, 2)
            pygame.draw.circle(entry, (*core, int(160 * (1.0 - intro_s))), (cx, cy), max(2, int(self.radius * intro_s)))
            glow.blit(entry, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        surf.blit(glow, glow.get_rect(center=(self.x, self.y)))

def draw_boss_bar(surf: pygame.Surface, boss, font: pygame.font.Font):
    spec = boss.spec()
    accent = spec["accent"]
    core = spec["core"]
    dark = spec["dark"]
    body = spec["body"]
    art = spec.get("art", spec.get("attack", "aegis"))
    is_hell = spec.get("short") == "HELL"

    bar_w = 468
    bar_h = 58
    x = WIDTH // 2 - bar_w // 2
    y = 12
    panel = pygame.Rect(x, y, bar_w, bar_h)
    fill_ratio = clamp(boss.hp / max(1, boss.max_hp), 0.0, 1.0)
    pulse = 0.5 + 0.5 * math.sin(boss.phase_timer * (2.0 + boss.boss_id * 0.08))
    phase = max(1, int(getattr(boss, "phase", 1)))
    transition_progress = 0.0
    transition_duration = max(0.001, float(getattr(boss, "phase_transition_duration", 0.0) or 0.0))
    if transition_duration > 0.0:
        transition_progress = clamp(float(getattr(boss, "phase_transition_timer", transition_duration)) / transition_duration, 0.0, 1.0)
    transition_flash = 1.0 - ease_out_cubic(clamp(transition_progress, 0.0, 1.0))
    phase_glow = 0.22 + 0.14 * (phase - 1) + 0.34 * transition_flash

    bg = get_clear_surface((bar_w, bar_h), ("boss_bar_bg", boss.boss_id, bar_w, bar_h))
    if is_hell:
        draw_round_rect(bg, (26, 10, 10, 235), bg.get_rect(), radius=18)
        draw_round_rect(bg, (88, 18, 14, 205), bg.get_rect(), radius=18, width=2)
    else:
        draw_round_rect(bg, (12, 16, 26, 235), bg.get_rect(), radius=18)
        draw_round_rect(bg, (*dark, 190), bg.get_rect(), radius=18, width=2)

    rail = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    pygame.draw.rect(rail, (*accent, 40 + int(72 * phase_glow)), (12, 8, bar_w - 24, 5), border_radius=2)
    pygame.draw.rect(rail, (*core, 22 + int(24 * phase_glow)), (18, 14, bar_w - 36, 2), border_radius=1)
    pygame.draw.rect(rail, (*accent, 18 + int(30 * phase_glow)), (14, bar_h - 11, bar_w - 28, 2), border_radius=1)
    bg.blit(rail, (0, 0))

    fill_w = int((bar_w - 12) * fill_ratio)
    if fill_w > 0:
        fill_rect = pygame.Rect(6, 7, fill_w, bar_h - 14)
        draw_round_rect(bg, body, fill_rect, radius=14)
        draw_round_rect(bg, accent, fill_rect, radius=14, width=2)

        if is_hell:
            for i in range(8):
                xx = 14 + int((fill_w - 24) * ((i * 0.14 + boss.phase_timer * 0.42) % 1.0))
                pygame.draw.line(bg, (255, 224, 160, 120), (xx, 8), (xx - 10, bar_h - 8), 2)
            for i in range(4):
                yy = 12 + i * 10 + int(math.sin(boss.phase_timer * 6.0 + i) * 2)
                pygame.draw.arc(bg, (255, 126, 56, 170), (8, yy, fill_w - 12, 16), 0.0, math.pi, 2)
            pygame.draw.circle(bg, (255, 244, 210, 170), (max(18, fill_w - 18), 14), 3)
        elif art == "aegis":
            for i in range(5):
                xx = 16 + int((fill_w - 30) * ((i * 0.24 + boss.phase_timer * 0.18) % 1.0))
                pygame.draw.line(bg, (*core, 110), (xx, 10), (xx - 12, bar_h - 12), 2)
            pygame.draw.polygon(bg, (*accent, 220), [(fill_w - 20, 10), (fill_w - 10, 20), (fill_w - 20, 30), (fill_w - 30, 20)])
        elif art == "tempest":
            for i in range(5):
                yy = 10 + int((bar_h - 22) * ((i * 0.18 + boss.phase_timer * 0.4) % 1.0))
                pygame.draw.arc(bg, (*core, 150), (10, yy - 10, fill_w - 20, 18), 0.1, 3.0, 2)
            pygame.draw.line(bg, (*core, 170), (fill_w - 26, 8), (fill_w - 8, 34), 2)
            pygame.draw.line(bg, (*accent, 120), (fill_w - 34, 32), (fill_w - 10, 10), 1)
        elif art == "void":
            for i in range(4):
                rr = 10 + i * 4
                pygame.draw.circle(bg, (*accent, 130), (fill_w - 22, bar_h // 2), rr, 2)
            pygame.draw.circle(bg, (*core, 200), (fill_w - 22, bar_h // 2), 4)
        elif art == "chrono":
            for i in range(4):
                yy = 10 + i * 8
                pygame.draw.line(bg, (*accent, 120), (14, yy), (fill_w - 18, yy), 1)
            dial = pygame.Rect(max(14, fill_w - 34), 9, 18, 18)
            pygame.draw.circle(bg, (*core, 170), dial.center, 8, 2)
            ang = boss.phase_timer * (1.2 + 0.08 * phase)
            pygame.draw.line(bg, (*body, 220), dial.center, (dial.centerx + int(math.cos(ang) * 7), dial.centery + int(math.sin(ang) * 7)), 2)
        elif art == "prism":
            for i in range(5):
                x0 = 14 + i * 20
                pygame.draw.polygon(bg, (*core, 165), [(x0, 10), (x0 + 8, 18), (x0, 26), (x0 - 8, 18)])
            pygame.draw.line(bg, (*accent, 160), (fill_w - 20, 10), (fill_w - 8, 30), 2)
            pygame.draw.line(bg, (*accent, 160), (fill_w - 22, 30), (fill_w - 8, 12), 2)
        elif art == "bloom":
            for i in range(5):
                x0 = 12 + i * 20
                leaf_y = 10 + int((math.sin(boss.phase_timer * 2.4 + i) + 1) * 5)
                pygame.draw.ellipse(bg, (*accent, 150), (x0, leaf_y, 10, 18))
            pygame.draw.arc(bg, (*core, 170), (10, 8, max(24, fill_w - 20), bar_h - 16), 0.2, 2.9, 2)
        elif art == "ember":
            for i in range(6):
                x0 = 10 + i * 18
                crack = 10 + int((math.sin(boss.phase_timer * 6.0 + x0 * 0.18) + 1) * 4)
                pygame.draw.line(bg, (*accent, 150), (x0, 8), (x0 - crack // 2, bar_h - 10), 1)
                pygame.draw.line(bg, (*core, 80), (x0 + 4, 14), (x0 + 2, bar_h - 14), 1)
        elif art == "tide":
            for i in range(4):
                yy = 11 + i * 9 + int(math.sin(boss.phase_timer * 2.2 + i) * 2)
                pygame.draw.arc(bg, (*accent, 170), (10, yy - 4, max(20, fill_w - 20), 12), 0.0, math.pi, 2)
        elif art == "frost":
            for i in range(4):
                x0 = 12 + i * 24
                pygame.draw.line(bg, (*core, 150), (x0, 8), (x0 + 10, 34), 2)
                pygame.draw.line(bg, (*accent, 110), (x0 + 10, 34), (x0 + 22, 14), 1)
        elif art == "stellar":
            for i in range(3):
                pygame.draw.polygon(bg, (*core, 180), [(18 + i * 22, 10), (24 + i * 22, 20), (34 + i * 22, 24), (24 + i * 22, 28), (18 + i * 22, 38), (12 + i * 22, 28), (2 + i * 22, 24), (12 + i * 22, 20)])
        elif art == "obsidian":
            for i in range(5):
                x0 = 14 + i * 18
                pygame.draw.polygon(bg, (*core, 190), [(x0, 8), (x0 + 10, 18), (x0, 30), (x0 - 10, 18)])
        else:
            pygame.draw.arc(bg, (*core, 220), pygame.Rect(10, 8, max(28, fill_w - 20), bar_h - 16), 0.6, 5.6, 2)

        if transition_flash > 0:
            over = get_clear_surface((fill_w + 24, bar_h + 16), ("boss_bar_transition", boss.boss_id, fill_w, bar_h))
            pygame.draw.circle(over, (*accent, int(145 * transition_flash)), (fill_w // 2 + 12, bar_h // 2 + 8), 18 + int(24 * transition_flash), 3)
            pygame.draw.circle(over, (*core, int(190 * transition_flash)), (fill_w // 2 + 12, bar_h // 2 + 8), 8 + int(12 * transition_flash), 2)
            pygame.draw.line(over, (*core, int(150 * transition_flash)), (6, 8), (fill_w + 16, bar_h + 6), 2)
            pygame.draw.line(over, (*accent, int(120 * transition_flash)), (fill_w + 16, 8), (6, bar_h + 6), 2)
            bg.blit(over, (0, 0))

    frame = pygame.Rect(0, 0, bar_w, bar_h)
    draw_round_rect(bg, (255, 255, 255, 20), frame, radius=18, width=1)
    for i in range(3):
        mx = int(bar_w * (0.31 + i * 0.2))
        my = 7 + int(math.sin(boss.phase_timer * 3.0 + i) * 1.5)
        pygame.draw.circle(bg, (*accent, 200 if i < phase else 90), (mx, my), 3)
        if i < phase:
            pygame.draw.circle(bg, (*core, 120), (mx, my), 6, 1)

    emblem = pygame.Rect(2, 2, 40, 40)
    if art == "aegis":
        pygame.draw.circle(bg, (*accent, 170), emblem.center, 11, 2)
        pygame.draw.polygon(bg, (*core, 220), [(emblem.centerx, 10), (28, 18), (emblem.centerx, 28), (12, 18)])
    elif art == "tempest":
        pygame.draw.arc(bg, (*core, 220), emblem.inflate(-6, -6), 0.2, 5.2, 2)
    elif art == "void":
        pygame.draw.circle(bg, (*accent, 180), emblem.center, 10, 2)
        pygame.draw.circle(bg, (*core, 180), (emblem.centerx + 4, emblem.centery - 2), 3)
    elif art == "chrono":
        pygame.draw.circle(bg, (*accent, 180), emblem.center, 10, 2)
        pygame.draw.line(bg, (*core, 220), emblem.center, (emblem.centerx, emblem.top + 8), 2)
        pygame.draw.line(bg, (*core, 220), emblem.center, (emblem.right - 8, emblem.centery), 2)
    elif art == "prism":
        pygame.draw.polygon(bg, (*core, 220), [(18, 10), (28, 18), (18, 28), (8, 18)])
    elif art == "bloom":
        pygame.draw.ellipse(bg, (*core, 220), (12, 9, 14, 20))
    elif art == "ember":
        pygame.draw.polygon(bg, (*core, 220), [(18, 9), (26, 18), (18, 27), (10, 18)])
    elif art == "tide":
        pygame.draw.arc(bg, (*core, 220), emblem.inflate(-8, -10), 0.1, 3.0, 2)
    elif art == "frost":
        pygame.draw.polygon(bg, (*core, 220), [(18, 9), (26, 18), (18, 27), (10, 18)])
    elif art == "stellar":
        pygame.draw.polygon(bg, (*core, 220), [(18, 8), (22, 16), (30, 18), (22, 20), (18, 28), (14, 20), (6, 18), (14, 16)])
    elif art == "obsidian":
        pygame.draw.polygon(bg, (*core, 220), [(18, 8), (28, 18), (18, 28), (8, 18)])
    else:
        pygame.draw.arc(bg, (*core, 220), emblem.inflate(-8, -8), 0.6, 5.6, 2)

    spark_x = int(58 + (bar_w - 70) * fill_ratio)
    spark_y = 22 + int(math.sin(boss.phase_timer * (5.0 + boss.boss_id * 0.2)) * 4)
    pygame.draw.circle(bg, (*core, 200), (spark_x, spark_y), 2)
    pygame.draw.circle(bg, (*accent, 120), (spark_x, spark_y), 6, 1)
    shimmer_x = int((bar_w + 40) * ((boss.phase_timer * 0.18) % 1.0)) - 20
    pygame.draw.line(bg, (255, 255, 255, 28), (shimmer_x, 6), (shimmer_x + 100, 6), 2)

    label_font = get_cached_sysfont("arial", 12, bold=True)
    for i, tag in enumerate(("I", "II", "III")):
        tag_alpha = 230 if i < phase else 95
        tag_box = pygame.Rect(286 + i * 52, 31 + int(math.sin(boss.phase_timer * 2.6 + i) * 1.0), 28, 11)
        if is_hell:
            pygame.draw.rect(bg, (120 + i * 20, 24, 16, tag_alpha), tag_box, border_radius=5)
            pygame.draw.rect(bg, (255, 176, 120, 150 if i < phase else 70), tag_box, border_radius=5, width=1)
        else:
            pygame.draw.rect(bg, (*accent, tag_alpha), tag_box, border_radius=5)
            pygame.draw.rect(bg, (*core, 120 if i < phase else 60), tag_box, border_radius=5)
        txt = render_text_cached(label_font, tag, WHITE if i < phase else (220, 230, 240))
        bg.blit(txt, txt.get_rect(center=tag_box.center))

    surf.blit(bg, panel.topleft)
    draw_text(surf, font, spec['short'], (panel.centerx, panel.centery - 1), WHITE, center=True, shadow=False)
    hp_text = f"{max(0, boss.hp)}/{boss.max_hp}"
    draw_text(surf, get_cached_sysfont("arial", 15, bold=True), hp_text, (panel.right - 12, panel.centery - 1), core, center=False, align="right", shadow=False)

@dataclass(slots=True)
class Boss:

    hp: int
    max_hp: int
    boss_id: int = 0
    x: float = WIDTH + 120
    y: float = HEIGHT * 0.46
    vx: float = -45.0
    phase: int = 1
    attack_timer: float = 0.0
    phase_timer: float = 0.0
    wobble: float = 0.0
    enraged: bool = False
    pulse: float = 0.0
    dying: bool = False
    death_timer: float = 0.0
    death_duration: float = 2.6
    death_shake: float = 0.0
    phase_transition_timer: float = 0.0
    phase_transition_duration: float = 0.0
    phase_changed: bool = False
    phase_from: int = 1
    phase_to: int = 1

    def spec(self) -> dict:
        return BOSS_SPECS[self.boss_id % len(BOSS_SPECS)]

    def health_ratio(self) -> float:
        return clamp(self.hp / max(1, self.max_hp), 0.0, 1.0)

    def desired_phase_from_hp(self) -> int:
        ratio = self.health_ratio()
        phase = 1
        if ratio <= 0.66:
            phase = 2
        if ratio <= 0.33:
            phase = 3
        return phase

    def sync_phase_with_hp(self):
        desired = self.desired_phase_from_hp()
        while self.phase < desired and not self.dying:
            self.trigger_phase_change(self.phase + 1)

    def start_death(self, duration: float = 2.6):
        self.dying = True
        self.death_timer = 0.0
        self.death_duration = max(0.8, float(duration))
        self.death_shake = 0.0
        self.attack_timer = 0.0
        self.phase_changed = False
        self.phase_transition_timer = 0.0
        self.phase_transition_duration = 0.0

    def trigger_phase_change(self, new_phase: int):
        new_phase = int(new_phase)
        if new_phase == self.phase or self.dying:
            return
        self.phase_from = int(self.phase)
        self.phase_to = new_phase
        self.phase = new_phase
        self.phase_changed = True
        self.phase_transition_timer = 0.0
        # Phase transitions are now driven purely by HP ratios, so the timing can
        # stay cinematic even when the total boss HP changes.
        self.phase_transition_duration = 1.18 if self.spec().get("short") == "HELL" else (0.96 if new_phase == 2 else 1.08)
        self.attack_timer = 0.0
        self.pulse += 1.35 if self.spec().get("short") == "HELL" else 1.0
        self.wobble += 0.68 if self.spec().get("short") == "HELL" else 0.45

    def update_death(self, dt: float):
        if not self.dying:
            return
        self.death_timer = min(self.death_duration, self.death_timer + dt)
        self.phase_timer += dt
        self.wobble += dt * 4.0
        self.pulse += dt * 5.0
        self.phase_transition_timer = min(self.phase_transition_duration, self.phase_transition_timer + dt)
        self.death_shake = max(self.death_shake, 0.18 * (1.0 - self.death_timer / max(0.001, self.death_duration)))

    def death_finished(self) -> bool:
        return self.dying and self.death_timer >= self.death_duration

    def draw_death(self, surf: pygame.Surface, font: pygame.font.Font):
        spec = self.spec()
        art = spec.get("art", spec.get("attack", "aegis"))
        progress = clamp(self.death_timer / max(0.001, self.death_duration), 0.0, 1.0)
        eased = ease_out_cubic(progress)
        fade = int(255 * (1.0 - progress))
        base_scale = lerp(1.08, 0.42, eased)

        img, _ = draw_boss_body_surface(spec, self)
        if art == "void":
            spin = math.sin(self.death_timer * 6.0) * 9.0
            scale = base_scale * lerp(1.0, 0.62, eased)
        elif art == "prism":
            spin = math.sin(self.death_timer * 7.0) * 15.0
            scale = base_scale * lerp(1.0, 1.12, 1.0 - progress)
        elif art == "tempest":
            spin = math.sin(self.death_timer * 10.0) * 24.0
            scale = base_scale * lerp(1.0, 0.90, eased)
        elif art == "stellar":
            spin = math.sin(self.death_timer * 5.0) * 6.0
            scale = base_scale * lerp(1.0, 0.58, eased)
        elif art == "ember":
            spin = math.sin(self.death_timer * 13.0) * 10.0
            scale = base_scale * lerp(1.0, 0.86, eased)
            if spec.get("short") == "HELL":
                spin = math.sin(self.death_timer * 16.0) * 18.0
                scale = base_scale * lerp(1.14, 0.32, eased)
        else:
            spin = math.sin(self.death_timer * 9.0) * 12.0 * (1.0 - progress)
            scale = base_scale
        img = pygame.transform.rotozoom(img, spin, scale)
        img.set_alpha(fade)

        ox = int(math.sin(self.death_timer * 9.5) * (4 + 10 * (1.0 - progress)))
        oy = int(math.cos(self.death_timer * 7.5) * (3 + 8 * (1.0 - progress)))
        surf.blit(img, img.get_rect(center=(self.x + ox, self.y + oy)))

        fx = get_clear_surface((520, 380), ("boss_death_fx", spec.get("short", spec.get("art", "aegis"))))
        cx = 260
        cy = 190
        accent = spec["accent"]
        core = spec["core"]
        dark = spec["dark"]

        def a(col, alpha):
            return (*col, max(0, int(alpha)))

        def line(points, col, width=2):
            pygame.draw.lines(fx, col, False, points, width)

        if art == "aegis":
            for i in range(4):
                r = int(58 + progress * (58 + i * 18))
                pygame.draw.circle(fx, a(accent, 180 - i * 30), (cx, cy), r, 4 - min(i, 2))
            for i in range(10):
                ang = self.death_timer * 2.5 + i * (math.tau / 10)
                dist = 32 + progress * 140
                px = cx + int(math.cos(ang) * dist)
                py = cy + int(math.sin(ang) * dist * 0.72)
                size = max(4, int(14 - progress * 7))
                pygame.draw.polygon(fx, a(core, 220 * (1.0 - progress)), [(px, py - size), (px + size, py), (px, py + size), (px - size, py)])
            for i in range(6):
                ang = self.death_timer * 4.2 + i * (math.tau / 6)
                x1 = cx + int(math.cos(ang) * 26)
                y1 = cy + int(math.sin(ang) * 18)
                x2 = cx + int(math.cos(ang) * (96 + progress * 62))
                y2 = cy + int(math.sin(ang) * (64 + progress * 42))
                pygame.draw.line(fx, a(core, 200), (x1, y1), (x2, y2), 3)

        elif art == "tempest":
            for i in range(7):
                yy = 54 + i * 36 + int(math.sin(self.death_timer * 5.0 + i) * 10)
                pygame.draw.arc(fx, a(core, 200 - i * 18), (-30, yy, 620, 58), 0.1 + progress * 0.4, 2.7 + progress * 0.8, 4 - (i % 2))
            for i in range(18):
                ang = self.death_timer * 7.0 + i * (math.tau / 18)
                dist = 20 + progress * 180
                x1 = cx + int(math.cos(ang) * 18)
                y1 = cy + int(math.sin(ang) * 18 * 0.72)
                x2 = cx + int(math.cos(ang) * dist)
                y2 = cy + int(math.sin(ang) * dist * 0.72)
                pygame.draw.line(fx, a(accent, 160), (x1, y1), (x2, y2), 2)
            for i in range(8):
                px = cx + int(math.cos(self.death_timer * 6.2 + i) * (80 + i * 3))
                py = cy + int(math.sin(self.death_timer * 4.8 + i) * (46 + i * 2))
                pygame.draw.polygon(fx, a(core, 170), [(px, py - 10), (px + 18, py), (px + 4, py + 12), (px - 14, py + 2)])

        elif art == "void":
            for i in range(5):
                r = int(48 + progress * (70 + i * 22))
                pygame.draw.circle(fx, a(accent, 170 - i * 22), (cx, cy), r, 2)
            pygame.draw.circle(fx, a(dark, 220), (cx, cy), int(22 + progress * 78))
            pygame.draw.circle(fx, a(core, 200), (cx, cy), int(max(4, 18 - progress * 10)), 2)
            for i in range(14):
                ang = self.death_timer * 3.0 + i * (math.tau / 14)
                bend = 0.22 + progress * 0.48
                pts = []
                for j in range(10):
                    tt = j / 9.0
                    radius = 26 + tt * (168 + progress * 56)
                    a0 = ang + tt * (1.2 + bend)
                    pts.append((cx + int(math.cos(a0) * radius), cy + int(math.sin(a0) * radius * 0.72)))
                line(pts, a(core, 180), 2)

        elif art == "chrono":
            for i in range(2):
                r = int(64 + progress * (90 + i * 14))
                pygame.draw.circle(fx, a(accent, 180 - i * 30), (cx, cy), r, 3)
            for i in range(12):
                ang = i * (math.tau / 12) + self.death_timer * 1.5
                x1 = cx + int(math.cos(ang) * 36)
                y1 = cy + int(math.sin(ang) * 36)
                x2 = cx + int(math.cos(ang) * (112 + progress * 72))
                y2 = cy + int(math.sin(ang) * (112 + progress * 72))
                pygame.draw.line(fx, a(core, 190), (x1, y1), (x2, y2), 2)
            for hand_ang, width, length in [(self.death_timer * 0.8, 5, 76), (self.death_timer * 2.6, 3, 112)]:
                ex = cx + int(math.cos(hand_ang) * length)
                ey = cy + int(math.sin(hand_ang) * length)
                pygame.draw.line(fx, a(core, 220), (cx, cy), (ex, ey), width)
            for i in range(8):
                ang = self.death_timer * 4.0 + i * (math.tau / 8)
                px = cx + int(math.cos(ang) * (88 + i * 2))
                py = cy + int(math.sin(ang) * (88 + i * 2) * 0.72)
                pts = [(px, py - 9), (px + 9, py), (px, py + 9), (px - 9, py)]
                pygame.draw.polygon(fx, a(accent, 200), pts)

        elif art == "prism":
            for i in range(7):
                ang = self.death_timer * 2.0 + i * (math.tau / 7)
                dist = 44 + progress * (126 + i * 8)
                x2 = cx + int(math.cos(ang) * dist)
                y2 = cy + int(math.sin(ang) * dist * 0.72)
                pygame.draw.line(fx, a(core, 190), (cx, cy), (x2, y2), 3)
            for i in range(5):
                s = 18 + i * 5
                ang = self.death_timer * 3.2 + i * 0.9
                px = cx + int(math.cos(ang) * (72 + progress * 54))
                py = cy + int(math.sin(ang) * (46 + progress * 34))
                pts = [(px, py - s), (px + s, py), (px, py + s), (px - s, py)]
                pygame.draw.polygon(fx, a(accent, 160 - i * 18), pts)
                pygame.draw.polygon(fx, a(core, 200), pts, 2)
            pygame.draw.polygon(fx, a(core, 180), [(cx, cy - 34), (cx + 62, cy), (cx, cy + 34), (cx - 62, cy)])

        elif art == "bloom":
            petal_count = 10
            for i in range(petal_count):
                ang = i * (math.tau / petal_count) + self.death_timer * 0.28
                dist = 46 + progress * 86
                px = cx + int(math.cos(ang) * dist)
                py = cy + int(math.sin(ang) * dist * 0.74)
                w = 18 + int(progress * 14)
                h = 42 + int(progress * 20)
                petal = pygame.Surface((w * 2 + 8, h * 2 + 8), pygame.SRCALPHA)
                pygame.draw.ellipse(petal, a(accent, 180 - i * 10), (4, 4, w * 2, h * 2))
                petal = pygame.transform.rotozoom(petal, math.degrees(ang) + self.death_timer * 10.0, 1.0)
                surf.blit(petal, petal.get_rect(center=(self.x + px - cx, self.y + py - cy)))
            for i in range(6):
                y = cy + 8 + i * 20
                pygame.draw.arc(fx, a(core, 170 - i * 18), (70, y, 380, 56), 0.0, math.pi, 3)
            for i in range(8):
                ang = self.death_timer * 2.4 + i * (math.tau / 8)
                x2 = cx + int(math.cos(ang) * (70 + progress * 86))
                y2 = cy + int(math.sin(ang) * (50 + progress * 62))
                pygame.draw.line(fx, a(core, 170), (cx, cy), (x2, y2), 2)

        elif art == "ember":
            for i in range(16):
                ang = self.death_timer * 5.0 + i * (math.tau / 16)
                dist = 24 + progress * (176 + i * 7)
                x2 = cx + int(math.cos(ang) * dist)
                y2 = cy + int(math.sin(ang) * dist * 0.62)
                pygame.draw.line(fx, a(accent, 220), (cx, cy), (x2, y2), 3)
            for i in range(7):
                r = int(42 + progress * (44 + i * 16))
                pygame.draw.circle(fx, a(core if i % 2 == 0 else accent, 180 - i * 16), (cx, cy + 18), r, 4 - min(i, 2))
            for i in range(24):
                x = 84 + i * 16 + int(math.sin(self.death_timer * 7.2 + i) * 7)
                y = 108 + int(math.sin(self.death_timer * 6.2 + i * 0.7) * 18)
                pygame.draw.circle(fx, a(core, 190), (x, y), 2)
            for i in range(10):
                ang = self.death_timer * 4.2 + i * (math.tau / 10)
                rr = 132 + int(12 * math.sin(self.death_timer * 4.0 + i))
                x1 = cx + int(math.cos(ang) * 18)
                y1 = cy + int(math.sin(ang) * 18 * 0.62)
                x2 = cx + int(math.cos(ang) * rr)
                y2 = cy + int(math.sin(ang) * rr * 0.62)
                pygame.draw.line(fx, a((255, 120, 54), 170), (x1, y1), (x2, y2), 2)
            pygame.draw.polygon(fx, a(dark, 210), [(114, 270), (162, 226), (208, 282), (244, 222), (306, 270), (268, 338), (214, 312), (172, 344)])

        elif art == "tide":
            for i in range(7):
                yy = 82 + i * 24 + int(math.sin(self.death_timer * 4.0 + i) * 8)
                pygame.draw.arc(fx, a(core, 180 - i * 18), (-40, yy, 640, 70), math.pi * 0.06, math.pi * 0.94, 3)
            for i in range(12):
                ang = self.death_timer * 3.0 + i * (math.tau / 12)
                dist = 36 + progress * 120
                x2 = cx + int(math.cos(ang) * dist)
                y2 = cy + int(math.sin(ang) * dist * 0.72)
                pygame.draw.circle(fx, a(core, 190), (x2, y2), max(2, 8 - i // 3))
            pygame.draw.arc(fx, a(accent, 200), (72, 72, 376, 200), 0.2 + progress * 0.3, 2.8 + progress * 0.5, 4)
            pygame.draw.arc(fx, a(core, 170), (110, 102, 300, 142), 0.0, math.pi, 2)

        elif art == "frost":
            for i in range(12):
                ang = self.death_timer * 2.5 + i * (math.tau / 12)
                dist = 30 + progress * (150 + i * 4)
                px = cx + int(math.cos(ang) * dist)
                py = cy + int(math.sin(ang) * dist * 0.72)
                s = 12 + (i % 3) * 4
                pygame.draw.polygon(fx, a(core, 210 - i * 12), [(px, py - s), (px + s, py), (px, py + s), (px - s, py)])
                pygame.draw.line(fx, a(accent, 170), (cx, cy), (px, py), 2)
            for i in range(6):
                r = int(50 + progress * (70 + i * 10))
                pygame.draw.circle(fx, a(accent, 170 - i * 20), (cx, cy), r, 2)
            for i in range(10):
                x = 94 + i * 34
                pygame.draw.line(fx, a(core, 180), (x, 66), (x + 8, 344), 1)

        elif art == "stellar":
            for i in range(14):
                ang = i * (math.tau / 14) + self.death_timer * 0.9
                dist = 18 + progress * (180 + i * 4)
                x2 = cx + int(math.cos(ang) * dist)
                y2 = cy + int(math.sin(ang) * dist * 0.72)
                pygame.draw.line(fx, a(core, 210), (cx, cy), (x2, y2), 3)
            for i in range(3):
                pygame.draw.circle(fx, a(accent, 170 - i * 36), (cx, cy), int(28 + progress * (48 + i * 22)), 3)
            for i in range(7):
                ang = self.death_timer * 1.5 + i * (math.tau / 7)
                px = cx + int(math.cos(ang) * (88 + i * 6))
                py = cy + int(math.sin(ang) * (64 + i * 4))
                pygame.draw.circle(fx, a(core, 210), (px, py), 5)
                pygame.draw.line(fx, a(accent, 180), (cx, cy), (px, py), 1)

        elif art == "obsidian":
            for i in range(16):
                ang = self.death_timer * 4.0 + i * (math.tau / 16)
                dist = 26 + progress * (170 + i * 5)
                px = cx + int(math.cos(ang) * dist)
                py = cy + int(math.sin(ang) * dist * 0.72)
                s = 8 + (i % 4) * 2
                pygame.draw.polygon(fx, a(core, 200 - i * 8), [(px, py - s), (px + s, py), (px, py + s), (px - s, py)])
            for i in range(6):
                x = 80 + i * 68 + int(math.sin(self.death_timer * 6.0 + i) * 8)
                pygame.draw.line(fx, a(accent, 180), (x, 60), (520 - x, 340), 2)
            pygame.draw.circle(fx, a(dark, 230), (cx, cy), int(30 + progress * 72))

        else:  # aurora
            for i in range(6):
                x = 84 + i * 66 + int(math.sin(self.death_timer * 2.2 + i) * 8)
                pygame.draw.arc(fx, a(accent, 190 - i * 18), (x, 64, 150, 240), 0.3 + progress * 0.2, 2.6 + progress * 0.4, 4)
            for i in range(12):
                ang = self.death_timer * 2.1 + i * (math.tau / 12)
                dist = 24 + progress * (150 + i * 4)
                px = cx + int(math.cos(ang) * dist)
                py = cy + int(math.sin(ang) * dist * 0.78)
                pygame.draw.circle(fx, a(core, 180 - i * 10), (px, py), 3)
            for i in range(3):
                pygame.draw.arc(fx, a(core, 150 - i * 18), (68, 90 + i * 20, 384, 120), 0.1, math.pi - 0.1, 3)

        pulse = 0.5 + 0.5 * math.sin(self.death_timer * 12.0)
        pygame.draw.circle(fx, (255, 255, 255, int(130 * (1.0 - progress) * pulse)), (cx, cy), int(24 + progress * 24), 2)

        fx.set_alpha(fade)
        surf.blit(fx, fx.get_rect(center=(self.x + int(math.sin(self.death_timer * 9.5) * (4 + 10 * (1.0 - progress))), self.y + int(math.cos(self.death_timer * 7.5) * (3 + 8 * (1.0 - progress))))))

    def update(self, dt: float, difficulty: Difficulty, pipes: List[Pipe], projectiles: List[BossProjectile], orbs: List[Orb], score: int):

        if self.dying:
            self.update_death(dt)
            return
        spec = self.spec()
        self.phase_changed = False
        self.phase_timer += dt
        self.wobble += dt * (2.0 + self.boss_id * 0.14)
        self.pulse += dt * (2.1 + self.boss_id * 0.16)
        self.x = lerp(self.x, WIDTH - 220, min(1.0, dt * 0.60))
        # ── Per-boss themed movement / hover style ───────────────────────────
        art = spec.get("art", "aegis")
        t = self.phase_timer
        rage_amp = 1.0 + 0.22 * max(0, self.phase - 1) + (0.18 if self.enraged else 0.0)

        if spec.get("name") == "HELL":
            # Hell: chaotic overlapping frequencies, increasingly frantic
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * (2.9 + self.boss_id * 0.12) + math.sin(t * 3.1) * 0.45) * (20 + self.phase * 7 + self.boss_id * 1.4) * rage_amp
        elif art == "aegis":
            # Aegis: slow sentinel hover, dignified and steady
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 1.4) * (10 + self.phase * 3) * rage_amp
        elif art == "tempest":
            # Tempest: erratic gusty jolts, windswept turbulence
            gust = math.sin(t * 4.8) * 0.55 + math.sin(t * 1.9) * 0.28
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 2.6 + gust) * (15 + self.phase * 5) * rage_amp
        elif art == "void":
            # Void: slow gravity-well, occasional surge
            pull = math.sin(t * 0.55) * 0.45
            self.y = HEIGHT * 0.44 + pull * 26 + math.sin(self.wobble * 1.1 + pull) * (13 + self.phase * 4) * rage_amp
        elif art == "chrono":
            # Chrono: mechanical tick — discretised step motion
            tick_speed = 1.2 + self.phase * 0.2
            tick_raw = self.wobble * tick_speed
            tick_step = math.floor(tick_raw * 3.0) / 3.0
            self.y = HEIGHT * 0.44 + math.sin(tick_step) * (11 + self.phase * 3) * rage_amp
        elif art == "prism":
            # Prism: smooth two-frequency glide, light diffraction drift
            self.y = HEIGHT * 0.44 + (math.sin(self.wobble * 1.6) * (10 + self.phase * 3) + math.cos(self.wobble * 0.75) * 4.5) * rage_amp
        elif art == "bloom":
            # Bloom: gentle plant sway, soft breeze rhythm
            sway = math.sin(t * 0.65) * 0.28
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 1.25 + sway) * (9 + self.phase * 3) * rage_amp
        elif art == "ember":
            # Ember: fiery upward thrust then free-fall drop
            thrust = abs(math.sin(self.wobble * 1.9))
            self.y = HEIGHT * 0.44 - thrust * (13 + self.phase * 4) * rage_amp + math.sin(self.wobble * 3.4) * 5
        elif art == "tide":
            # Tide: layered wave rhythm like ocean swells
            self.y = HEIGHT * 0.44 + (math.sin(self.wobble * 1.5) * (13 + self.phase * 4) + math.sin(self.wobble * 2.9) * 4.5) * rage_amp
        elif art == "frost":
            # Frost: slow crystalline, occasional near-freeze pause
            slow_wave = math.sin(self.wobble * 1.2) * (10 + self.phase * 3)
            freeze = max(0.0, math.cos(t * 0.48)) ** 5  # occasional stillness
            self.y = HEIGHT * 0.44 + slow_wave * (1.0 - freeze * 0.65) * rage_amp
        elif art == "stellar":
            # Stellar: orbital elliptical path
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 1.7) * math.cos(self.wobble * 0.28) * (13 + self.phase * 4) * rage_amp
        elif art == "obsidian":
            # Obsidian: sharp angular jolts
            angle_t = self.wobble * 2.2
            jolt = (math.sin(angle_t * 3.2) ** 3) * 8
            self.y = HEIGHT * 0.44 + (math.sin(angle_t) * (12 + self.phase * 4) + jolt) * rage_amp
        elif art == "aurora":
            # Aurora: ribbon-like flowing, nested sines
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 1.35 + math.sin(self.wobble * 0.48) * 1.3) * (12 + self.phase * 4) * rage_amp
        elif art == "nova":
            # Nova: cosmic expanding/contracting pulse
            expand = 0.5 + 0.5 * math.sin(t * 0.75)
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 1.6) * (8 + expand * 11 + self.phase * 4) * rage_amp
        elif art == "rift":
            # Rift: stutter-teleport effect via cubed sine
            stutter = (math.sin(self.wobble * 4.1)) ** 3
            self.y = HEIGHT * 0.44 + (stutter * (18 + self.phase * 5) + math.sin(self.wobble * 1.25) * 5) * rage_amp
        elif art == "thorn":
            # Thorn: coiling vine multi-frequency
            self.y = HEIGHT * 0.44 + (math.sin(self.wobble * 1.5) * (11 + self.phase * 3) + math.cos(self.wobble * 2.7) * 5.5) * rage_amp
        elif art == "sentinel":
            # Sentinel: slow precision patrol, very deliberate
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * 0.95) * (9 + self.phase * 3) * rage_amp
        else:
            self.y = HEIGHT * 0.44 + math.sin(self.wobble * (2.0 + self.boss_id * 0.12)) * (12 + self.phase * 4 + self.boss_id * 1.2) * rage_amp
        # ─────────────────────────────────────────────────────────────────────

        self.attack_timer += dt
        if self.phase_transition_duration > 0.0 and self.phase_transition_timer < self.phase_transition_duration:
            self.phase_transition_timer = min(self.phase_transition_duration, self.phase_transition_timer + dt * (1.15 + 0.08 * self.phase))

        periods = spec.get("periods", {})
        if difficulty.name in periods:
            slow, fast = periods[difficulty.name]
        else:
            slow, fast = periods.get("NORMAL", (1.8, 1.0))
        period = lerp(slow, fast, 1 - self.health_ratio())
        period *= 1.02 if self.phase == 1 else 0.96 if self.phase == 2 else 0.90
        if difficulty.name == "INSANE":
            period *= 0.88
        if spec.get("name") == "HELL":
            period *= 0.76
        if self.attack_timer >= period:
            self.attack_timer = 0.0
            self.spawn_attack(difficulty, pipes, projectiles)

        desired_phase = self.desired_phase_from_hp()
        if desired_phase >= 3:
            self.enraged = True
        if desired_phase > self.phase:
            self.sync_phase_with_hp()
            if spec.get("name") == "HELL":
                self.attack_timer = 0.42 if self.phase >= 3 else 0.28

    def _target_pipe(self, pipes: List[Pipe]) -> Optional[Pipe]:
        if not pipes:
            return None
        candidates = [p for p in pipes if p.x + p.width > self.x - 120]
        return min(candidates or pipes, key=lambda p: abs((p.x + p.width * 0.5) - self.x))

    def _spawn_projectile(self, projectiles: List[BossProjectile], x: float, y: float, vx: float, vy: float, radius: int):
        # Cap vertical drift so a projectile can't cross the full pipe gap during
        # its screen transit — prevents bullets from sealing the only exit.
        vy = clamp(float(vy), -50.0, 50.0)
        projectiles.append(BossProjectile(x, y, vx, vy, radius, kind=self.spec().get("projectile", self.spec()["attack"]), boss_id=self.boss_id))

    def spawn_attack(self, difficulty: Difficulty, pipes: List[Pipe], projectiles: List[BossProjectile]):
        target_pipe = self._target_pipe(pipes)
        if target_pipe is None:
            return

        spec = self.spec()
        gap_top = target_pipe.gap_y - target_pipe.gap_size * 0.5
        gap_bottom = target_pipe.gap_y + target_pipe.gap_size * 0.5
        # Safety = minimum distance from gap edge where projectiles may spawn.
        # Must account for projectile radius (~10 px) + reaction room for the player.
        # Larger margins on easier modes; INSANE stays tight but still passable.
        safety = 44 if difficulty.name == "EASY" else 38 if difficulty.name == "NORMAL" else 32
        if difficulty.name == "INSANE":
            safety = 26
        # Enforce a minimum lane height so the lane is actually usable
        min_lane_h = 36
        safe_lanes = []
        if gap_top > 120:
            upper_hi = max(70, gap_top - safety)
            if upper_hi - 70 >= min_lane_h:
                safe_lanes.append((70, upper_hi))
        if gap_bottom < HEIGHT - 90:
            lower_lo = min(HEIGHT - 90, gap_bottom + safety)
            if HEIGHT - 92 - lower_lo >= min_lane_h:
                safe_lanes.append((lower_lo, HEIGHT - 92))
        if not safe_lanes:
            safe_lanes = [(70, 140), (HEIGHT - 150, HEIGHT - 92)]

        speeds = spec.get("speeds", {})
        base_speed = speeds.get(difficulty.name, speeds.get("NORMAL", 156))
        speed = (base_speed + self.phase * (20 + self.boss_id)) * 0.92
        speed += difficulty.pipe_speed * 0.08
        if difficulty.name == "INSANE":
            speed *= 1.08
        # Spawn bullets far enough past the pipe exit that the bird has room to
        # clear the gap before encountering the shot.  Extra offset on INSANE where
        # timing pressure is highest.
        x_offset = 28 if difficulty.name == "INSANE" else 18
        x = target_pipe.x + target_pipe.width + x_offset
        phase = self.phase
        family = spec.get("attack", "aegis")

        def lane_center(lane):
            return (lane[0] + lane[1]) * 0.5

        if family == "aegis":
            count = 1 if phase == 1 else 2 if phase == 2 else 3
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + random.randint(-12, 12), 110, HEIGHT - 110)
                vy = random.uniform(-9, 9) if phase < 3 else random.uniform(-13, 13)
                self._spawn_projectile(projectiles, x + i * 12, y, -speed, vy, 8 if difficulty.name == "EASY" else 9 if difficulty.name == "NORMAL" else 10)
        elif family == "tempest":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            spread = 0.8 if phase == 1 else 1.0 if phase == 2 else 1.18
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = random.uniform(lane[0], lane[1])
                offset = (i - (count - 1) / 2) * 0.48
                vy = offset * 44 * spread + random.uniform(-7, 7)
                self._spawn_projectile(projectiles, x + i * 8, y, -speed * (1.0 if phase < 3 else 1.06), vy, 8 if phase == 1 else 9)
        elif family == "void":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = random.uniform(lane[0], lane[1])
                swirl = math.sin(self.phase_timer * (2.0 + i * 0.16) + i) * (18 + phase * 4)
                vy = swirl + random.uniform(-10, 10)
                self._spawn_projectile(projectiles, x + i * 10, y, -speed * 1.05, vy, 8 if phase < 3 else 9)
        elif family == "chrono":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + math.sin(self.phase_timer * 3.0 + i) * 30, 96, HEIGHT - 96)
                vx = -speed * (1.0 + 0.04 * i)
                vy = random.uniform(-18, 18) + math.cos(self.phase_timer * 4.0 + i) * (12 + phase * 4)
                self._spawn_projectile(projectiles, x + i * 14, y, vx, vy, 8 if phase == 1 else 9 if phase == 2 else 10)
        elif family == "prism":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + (i - (count - 1) / 2) * 18, 102, HEIGHT - 102)
                vy = (i - (count - 1) / 2) * 30 + math.sin(self.phase_timer * 2.4 + i) * 10
                self._spawn_projectile(projectiles, x + i * 10, y, -speed * 1.02, vy, 8 if phase < 2 else 9 if phase == 2 else 10)
        elif family == "bloom":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = random.uniform(lane[0], lane[1])
                vy = math.sin(self.phase_timer * 2.2 + i) * (20 + phase * 4)
                if i % 2 == 0:
                    vy -= 10
                self._spawn_projectile(projectiles, x + i * 11, y, -speed * 0.98, vy, 8 if phase == 1 else 9)
        elif family == "ember":
            if spec.get("name") == "HELL":
                count = 4 if phase == 1 else 5 if phase == 2 else 6
                for i in range(count):
                    lane = safe_lanes[i % len(safe_lanes)]
                    y = clamp(lane_center(lane) + random.randint(-34, 34), 88, HEIGHT - 88)
                    # HELL should feel oppressive: denser lanes, faster falloff, and layered follow-up shots.
                    vy = random.uniform(14, 38) + phase * 7 + (i - (count - 1) / 2) * 4.0
                    radius = 8 if phase == 1 else 9 if phase == 2 else 10
                    self._spawn_projectile(projectiles, x + i * 10, y, -speed * 1.14, vy, radius)
                    if phase >= 2:
                        self._spawn_projectile(
                            projectiles,
                            x + 6 + i * 10,
                            clamp(y + random.randint(-12, 12), 84, HEIGHT - 84),
                            -speed * 0.95,
                            -vy * 0.56 + random.uniform(-6, 6),
                            max(6, radius - 1),
                        )
                    if phase >= 3 and i % 2 == 0:
                        flank_y = clamp(y + (28 if i % 4 == 0 else -28), 84, HEIGHT - 84)
                        self._spawn_projectile(
                            projectiles,
                            x + 18 + i * 8,
                            flank_y,
                            -speed * 1.20,
                            vy * 0.30 + (16 if i % 4 == 0 else -16),
                            max(6, radius - 2),
                        )
            else:
                count = 2 if phase == 1 else 3 if phase == 2 else 4
                for i in range(count):
                    lane = safe_lanes[i % len(safe_lanes)]
                    y = clamp(lane_center(lane) + random.randint(-20, 20), 96, HEIGHT - 96)
                    vy = random.uniform(8, 28) + phase * 4
                    self._spawn_projectile(projectiles, x + i * 12, y, -speed * 1.04, vy, 8 if phase < 3 else 9)
        elif family == "tide":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + math.sin(self.phase_timer * 2.3 + i) * 32, 100, HEIGHT - 100)
                vy = math.cos(self.phase_timer * 2.0 + i) * (16 + phase * 4)
                self._spawn_projectile(projectiles, x + i * 14, y, -speed * 0.98, vy, 8 if phase == 1 else 9 if phase == 2 else 10)
        elif family == "frost":
            count = 3 if phase == 1 else 4 if phase == 2 else 5
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = random.uniform(lane[0], lane[1])
                vy = (i - (count - 1) / 2) * 18 + math.sin(self.phase_timer * 3.2 + i) * 10
                self._spawn_projectile(projectiles, x + i * 10, y, -speed * 1.08, vy, 7 if phase == 1 else 8 if phase == 2 else 9)
        elif family == "stellar":
            count = 3 if phase == 1 else 4 if phase == 2 else 5
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + math.sin(self.phase_timer * 1.7 + i) * 26, 98, HEIGHT - 98)
                vy = (i - (count - 1) / 2) * 22 + math.cos(self.phase_timer * 2.8 + i) * 10
                self._spawn_projectile(projectiles, x + i * 10, y, -speed * 1.03, vy, 8 if phase == 1 else 9)
        elif family == "obsidian":
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + random.randint(-14, 14), 98, HEIGHT - 98)
                vy = random.uniform(-6, 12) + phase * 3
                self._spawn_projectile(projectiles, x + i * 14, y, -speed * 1.00, vy, 9 if phase < 3 else 10)
        else:  # aurora
            count = 2 if phase == 1 else 3 if phase == 2 else 4
            for i in range(count):
                lane = safe_lanes[i % len(safe_lanes)]
                y = clamp(lane_center(lane) + math.sin(self.phase_timer * 2.8 + i) * 22, 104, HEIGHT - 104)
                vy = math.sin(self.phase_timer * 3.2 + i) * (18 + phase * 3)
                self._spawn_projectile(projectiles, x + i * 12, y, -speed * 1.01, vy, 8 if phase == 1 else 9 if phase == 2 else 10)

    def draw(self, surf: pygame.Surface, font: pygame.font.Font, difficulty: Difficulty):
        if self.dying:
            self.draw_death(surf, font)
            draw_boss_bar(surf, self, font)
            return
        spec = self.spec()
        img, rect = draw_boss_body_surface(spec, self)
        surf.blit(img, rect)
        if self.phase_changed or (self.phase_transition_duration > 0 and self.phase_transition_timer < self.phase_transition_duration):
            transition = get_clear_surface((rect.width + 240, rect.height + 240), ("boss_phase_transition", self.boss_id, rect.width, rect.height))
            cx = transition.get_width() // 2
            cy = transition.get_height() // 2
            phase_progress = 0.0
            if self.phase_transition_duration > 0:
                phase_progress = clamp(self.phase_transition_timer / max(0.001, self.phase_transition_duration), 0.0, 1.0)
            burst = 1.0 - ease_out_cubic(phase_progress)
            accent = spec["accent"]
            core = spec["core"]
            dark = spec["dark"]
            for i in range(6):
                rr = int(38 + i * 24 + burst * (76 + i * 6))
                pygame.draw.circle(transition, (*accent, int(110 * burst * (1 - i * 0.12))), (cx, cy), rr, 3 if i < 4 else 2)
            for i in range(16):
                ang = self.phase_timer * (3.4 + i * 0.05) + i * (math.tau / 16)
                x1 = cx + int(math.cos(ang) * (18 + i * 2))
                y1 = cy + int(math.sin(ang) * (12 + i))
                x2 = cx + int(math.cos(ang) * (140 + burst * 72))
                y2 = cy + int(math.sin(ang) * (90 + burst * 44))
                pygame.draw.line(transition, (*core, int(120 * burst)), (x1, y1), (x2, y2), 2 if i % 3 == 0 else 1)
            for i in range(8):
                ang = self.phase_timer * 6.4 + i * (math.tau / 8)
                px = cx + int(math.cos(ang) * (54 + burst * 66))
                py = cy + int(math.sin(ang) * (36 + burst * 42))
                pygame.draw.circle(transition, (*dark, int(90 * burst)), (px, py), 3)
            if spec.get("short") == "HELL":
                for i in range(24):
                    ang = self.phase_timer * 8.4 + i * (math.tau / 24)
                    rr = 82 + int(36 * burst) + (i % 4) * 8
                    px = cx + int(math.cos(ang) * rr)
                    py = cy + int(math.sin(ang) * rr * 0.72)
                    pygame.draw.circle(transition, (255, 126, 50, int(200 * burst)), (px, py), 3)
                for i in range(7):
                    yy = cy - 96 + i * 34 + int(math.sin(self.phase_timer * 10.0 + i) * 8)
                    pygame.draw.arc(transition, (255, 220, 180, int(190 * burst)), (cx - 182, yy, 364, 22), 0.0, math.pi, 2)
                for i in range(10):
                    ang = self.phase_timer * 3.8 + i * (math.tau / 10)
                    rr = 132 + int(24 * burst)
                    px = cx + int(math.cos(ang) * rr)
                    py = cy + int(math.sin(ang) * rr * 0.68)
                    pygame.draw.line(transition, (255, 200, 120, int(160 * burst)), (cx, cy), (px, py), 2)
            surf.blit(transition, transition.get_rect(center=rect.center), special_flags=pygame.BLEND_RGBA_ADD)
        draw_boss_bar(surf, self, font)

@dataclass(slots=True)
class Cloud:
    x: float
    y: float
    scale: float
    speed: float
    kind: int

    def update(self, dt: float):
        self.x -= self.speed * dt

    def draw(self, surf: pygame.Surface, color: Tuple[int, int, int]):
        w = int(90 * self.scale)
        h = int(42 * self.scale)
        key = (w, h, color)
        cloud = _CLOUD_CACHE.get(key)
        if cloud is None:
            cloud = pygame.Surface((w + 40, h + 20), pygame.SRCALPHA)
            c = (*color, 180)
            pygame.draw.ellipse(cloud, c, (8, 10, w * 0.5, h * 0.72))
            pygame.draw.ellipse(cloud, c, (w * 0.25, 4, w * 0.45, h * 0.95))
            pygame.draw.ellipse(cloud, c, (w * 0.53, 12, w * 0.40, h * 0.68))
            _CLOUD_CACHE[key] = cloud
            _trim_cache(_CLOUD_CACHE, 256)
        surf.blit(cloud, (self.x, self.y))

EGG_MESSAGES = [
    "HELLO!!!.!/",
    'DO YOU KNOW WHO MADE THIS GAME FOR YOU TO PLAY??":U+',
    "IT'S ME!!!!_+}:",
    "THAT'S ALL--=_+_",
    'GOODBYE...._+:"?',
]
EGG_GLITCH_TEXT = "V - 3679+!PO@:>P!PH#OH(O#P!EUBINOKNNI"

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        # ── Resizable window: game always renders at native (WIDTH×HEIGHT) ──
        # self._window  = the real OS window (resizable / fullscreen)
        # self.screen   = fixed-size game surface – all draw calls target this
        self._window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.screen = pygame.Surface((WIDTH, HEIGHT)).convert()
        self._fullscreen = False
        self._cached_game_rect_size: Optional[Tuple[int, int]] = None
        self._cached_game_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.font_big = pygame.font.SysFont("arial", 34, bold=True)
        self.font_huge = pygame.font.SysFont("arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("arial", 17)
        self.font_tiny_bold = get_cached_sysfont("arial", 15, bold=True)
        self.font_micro = get_cached_sysfont("arial", 14)
        self.font_victory = pygame.font.SysFont("arial", 72, bold=True)

        self.sounds = SoundBank()
        self.sounds.init()

        self.bg_cache = {}
        for theme in THEMES:
            self.bg_cache[theme["name"]] = build_gradient_surface(theme["sky_top"], theme["sky_bottom"]).convert()
        for i, theme in enumerate(BOSS_THEMES):
            self.bg_cache[f"BOSS_{i}"] = build_gradient_surface(theme["sky_top"], theme["sky_bottom"]).convert()

        self.arcade_bg_cache = {}
        for i, theme in enumerate(THEMES):
            self.arcade_bg_cache[theme["name"]] = build_arcade_background_scene(theme, i)

        self.state = "MENU"
        self.running = True
        self.settings = self.load_settings()

        self.menu_index = 0
        self.pause = False
        self.current_mode = "ARCADE"
        self.current_difficulty_index = int(clamp(int(self.settings.get("last_difficulty", 1)), 0, len(DIFFICULTIES) - 1))
        legacy_selected = self.settings.get("selected_skin_name", self.settings.get("selected_skin", 0))
        self.selected_skin = self.resolve_skin_setting(legacy_selected)
        self.coins = int(self.settings.get("coins", 0))
        self.best_scores = self.load_best_scores(self.settings)
        self.sound_on = bool(self.settings.get("sound_on", True))
        self.sounds.set_enabled(self.sound_on)
        self.show_hitboxes = bool(self.settings.get("show_hitboxes", False))
        self.unlocked = self.load_unlocked_skins(self.settings)
        self.unlocked.add(0)
        self.skin_index = self.selected_skin if 0 <= self.selected_skin < len(SKINS) else 0
        self.selected_skin = self.skin_index
        self.boss_index = int(self.settings.get("last_boss", 0)) % len(BOSS_SPECS)
        self.menu_scroll = 0.0
        self.overlay_cache = {}
        self.hitbox_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._settings_dirty = False
        self._last_settings_save = 0.0
        self._settings_save_interval = 0.75
        self.profile_tab = str(self.settings.get("profile_tab", "stats")).lower()
        if self.profile_tab not in ("stats", "quests", "achievements"):
            self.profile_tab = "stats"
        self.profile_achievement_index = int(self.settings.get("profile_achievement_index", 0))
        self.profile_achievement_index = int(clamp(self.profile_achievement_index, 0, max(0, len(ACHIEVEMENT_SPECS) - 1)))

        self.profile_totals = self.load_profile_totals(self.settings)
        self.achievements = self.load_achievements(self.settings)
        self.quest_state = self.load_quest_state(self.settings)
        self.last_run_summary = self.settings.get("last_run_summary", {}) if isinstance(self.settings.get("last_run_summary", {}), dict) else {}
        self.pending_quest_reward = 0
        self.notifications = []

        self.reset_world()
        # Pre-allocated surface for boss entry fade (reused every frame, zero allocation).
        self._boss_entry_fade_surf = pygame.Surface((WIDTH, HEIGHT)).convert()
        self._boss_entry_fade_surf.fill((0, 0, 0))
        self.menu_items = ["PLAY", "SKINS", "Profile", "OPTIONS", "QUIT"]
        self.menu_page = "MAIN"
        self.play_index = 0
        self.options_index = 0
        self.options_reset_confirm = False
        self.options_reset_confirm_choice = 0
        self.skin_cursor = self.skin_index
        self.difficulty_cursor = self.current_difficulty_index
        self.difficulty_mode_target = "ARCADE"
        self.message = ""
        self.message_timer = 0.0
        self.ui_time = 0.0

        # Easter egg state
        self.egg_phase = None
        self.egg_timer = 0.0
        self.egg_msg_index = 0
        self.egg_matrix_cols: list = []
        self.egg_chaos_frames = 0
        self.egg_total_timer = 0.0
        self.egg_noise_channel = None
        self.egg_fx_strength = 0.0
        self.egg_bsod_entered = False
        self.egg_hex_offset = 0.0
        self.egg_chaos_surge_played = False
        self.egg_pixel_sparks: list = []
        self.egg_bsod_glitch_t = 0.0
        self.egg_char_h = 12

    def load_settings(self):
        if SAVE_FILE.exists():
            try:
                data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
        return {}

    def resolve_skin_setting(self, value) -> int:
        if isinstance(value, str):
            idx = skin_index_from_name(value)
            if idx != 0 or value.upper() == "CLASSIC":
                return idx
            try:
                return skin_index_from_legacy_index(int(value))
            except Exception:
                return 0
        try:
            idx = int(value)
        except Exception:
            return 0
        if 0 <= idx < len(SKINS):
            if idx == 0:
                return 0
            legacy_name = skin_name_from_legacy_index(idx)
            return skin_index_from_name(legacy_name)
        return 0

    def load_unlocked_skins(self, settings: dict):
        raw_names = settings.get("unlocked_names")
        if isinstance(raw_names, list) and raw_names:
            unlocked = set()
            for name in raw_names:
                unlocked.add(skin_index_from_name(name))
            return unlocked

        raw = settings.get("unlocked", [0])
        unlocked = set()
        if isinstance(raw, list):
            for item in raw:
                try:
                    idx = int(item)
                except Exception:
                    continue
                unlocked.add(skin_index_from_legacy_index(idx))
        return unlocked

    def load_best_scores(self, settings: dict) -> Dict[str, int]:
        raw = settings.get("best_scores", {})
        if isinstance(raw, dict):
            return {str(k): int(v) for k, v in raw.items()}
        legacy = settings.get("high_score", 0)
        return {self.best_score_key("ARCADE", DIFFICULTIES[1].name): int(legacy)}

    def best_score_key(self, mode: str, difficulty_name: str) -> str:
        if mode == "BOSS":
            return f"{mode}:{difficulty_name}:{self.boss_index}"
        return f"{mode}:{difficulty_name}"

    def current_best_score(self) -> int:
        return int(self.best_scores.get(self.best_score_key(self.current_mode, DIFFICULTIES[self.current_difficulty_index].name), 0))

    def set_best_score(self, value: int):
        key = self.best_score_key(self.current_mode, DIFFICULTIES[self.current_difficulty_index].name)
        self.best_scores[key] = max(int(self.best_scores.get(key, 0)), int(value))

    def set_sound_enabled(self, enabled: bool, *, play_feedback: bool = True):
        enabled = bool(enabled)
        changed = self.sound_on != enabled
        self.sound_on = enabled
        self.sounds.set_enabled(enabled)
        if enabled and changed and play_feedback:
            self.sounds.play("click")
        self.save_settings()

    def get_overlay(self, size: Tuple[int, int], color: Tuple[int, int, int, int]) -> pygame.Surface:
        # Bucket alpha values so animated fades/flash overlays reuse cached
        # surfaces instead of generating a new full-screen surface every frame.
        alpha = max(0, min(255, int(color[3])))
        alpha = (alpha // 8) * 8
        key = (size, (int(color[0]), int(color[1]), int(color[2]), alpha))
        overlay = self.overlay_cache.get(key)
        if overlay is None:
            overlay = pygame.Surface(size, pygame.SRCALPHA)
            overlay.fill(key[1])
            self.overlay_cache[key] = overlay
        return overlay

    def _flush_settings_save(self, force: bool = False):
        if not self._settings_dirty and not force:
            return
        now = pygame.time.get_ticks() / 1000.0
        if not force and (now - self._last_settings_save) < self._settings_save_interval:
            return

        data = {
            "selected_skin": self.selected_skin,
            "selected_skin_name": SKINS[self.selected_skin].name,
            "last_difficulty": self.current_difficulty_index,
            "coins": self.coins,
            "best_scores": self.best_scores,
            "sound_on": self.sound_on,
            "unlocked": sorted(self.unlocked),
            "unlocked_names": [SKINS[i].name for i in sorted(self.unlocked) if 0 <= i < len(SKINS)],
            "last_boss": self.boss_index,
            "profile_totals": self.profile_totals,
            "achievements": sorted(self.achievements),
            "quest_state": self.quest_state,
            "last_run_summary": self.last_run_summary,
            "profile_tab": self.profile_tab,
            "profile_achievement_index": self.profile_achievement_index,
            "show_hitboxes": self.show_hitboxes,
        }
        try:
            tmp_path = SAVE_FILE.with_name(SAVE_FILE.name + ".tmp")
            tmp_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            tmp_path.replace(SAVE_FILE)
            self._last_settings_save = now
            self._settings_dirty = False
        except Exception:
            pass

    def save_settings(self, force: bool = False):
        self._settings_dirty = True
        self._flush_settings_save(force=force)

    def default_profile_totals(self):
        return {
            "runs": 0,
            "wins": 0,
            "boss_wins": 0,
            "boss_wins_hard": 0,
            "deaths": 0,
            "flaps": 0,
            "pipes_scored": 0,
            "score_total": 0,
            "coins_collected": 0,
            "items_total": 0,
            "shield_breaks": 0,
            "boss_damage_dealt": 0,
            "play_time": 0.0,
            "daily_complete": 0,
            "weekly_complete": 0,
            "max_score": 0,
            "best_combo": 0,
            "item_counts": {},
        }

    def load_profile_totals(self, settings: dict):
        base = self.default_profile_totals()
        raw = settings.get("profile_totals", {})
        if isinstance(raw, dict):
            for key in base:
                if key == "item_counts":
                    continue
                if key in raw:
                    try:
                        base[key] = float(raw[key]) if key == "play_time" else int(raw[key])
                    except Exception:
                        pass
            item_counts = raw.get("item_counts", {})
            if isinstance(item_counts, dict):
                cleaned = {}
                for k, v in item_counts.items():
                    try:
                        iv = int(v)
                    except Exception:
                        continue
                    if iv > 0:
                        cleaned[str(k)] = iv
                base["item_counts"] = cleaned
        return base

    def load_achievements(self, settings: dict):
        raw = settings.get("achievements", [])
        if isinstance(raw, list):
            return {str(v) for v in raw}
        return set()

    def load_quest_state(self, settings: dict):
        raw = settings.get("quest_state", {})
        if isinstance(raw, dict):
            return raw
        return {}

    def quest_stat_value(self, stat: str) -> float:
        totals = self.profile_totals
        if stat.startswith("item:"):
            item = stat.split(":", 1)[1]
            return float(totals.get("item_counts", {}).get(item, 0))
        return float(totals.get(stat, 0))

    def build_quest(self, tier: str, spec: dict, rng: random.Random, idx: int):
        target = rng.randint(*spec["target"])
        reward = rng.randint(*spec["reward"])
        quest = {
            "id": f"{tier}:{spec['key']}:{idx}:{today_key() if tier == 'daily' else week_key()}",
            "tier": tier,
            "title": spec["title"],
            "desc": spec["desc"].format(target=target),
            "stat": spec["stat"],
            "target": int(target),
            "reward": int(reward),
            "start": self.quest_stat_value(spec["stat"]),
            "progress": 0,
            "completed": False,
            "claimed": False,
            "icon": spec["icon"],
        }
        return quest

    def build_quest_set(self, tier: str, key: str):
        rng = random.Random(f"{tier}:{key}:SkyPulse")
        pool = list(QUEST_TEMPLATES[tier])
        rng.shuffle(pool)
        chosen = pool[:3]
        return [self.build_quest(tier, spec, rng, i) for i, spec in enumerate(chosen)]

    def ensure_quest_state(self, force: bool = False):
        today = today_key()
        week = week_key()
        if force or self.quest_state.get("daily_key") != today:
            self.quest_state["daily_key"] = today
            self.quest_state["daily"] = self.build_quest_set("daily", today)
        if force or self.quest_state.get("weekly_key") != week:
            self.quest_state["weekly_key"] = week
            self.quest_state["weekly"] = self.build_quest_set("weekly", week)

    def achievement_value(self, stat: str) -> float:
        return self.quest_stat_value(stat)

    def unlock_achievement(self, key: str):
        if key not in self.achievements:
            self.achievements.add(key)
            spec = next((spec for spec in ACHIEVEMENT_SPECS if spec["key"] == key), None)
            name = spec["name"] if spec else key.replace("_", " ").title()
            desc = spec["desc"] if spec else ""
            self.add_text("ARCHIEVEMENT UNLOCK!", WIDTH * 0.5, 154, (255, 205, 92))
            self.queue_notification("ARCHIEVEMENT UNLOCK!", name if not desc else f"{name} • {desc}", (255, 168, 84), duration=3.2)
            self.sounds.play("win")
            return True
        return False

    def evaluate_meta(self, *, award_rewards: bool = True):
        self.ensure_quest_state()
        changed = False
        for tier in ("daily", "weekly"):
            quests = self.quest_state.get(tier, [])
            for quest in quests:
                current = self.quest_stat_value(quest.get("stat", ""))
                quest["progress"] = int(max(0, current - float(quest.get("start", 0))))
                if not quest.get("completed") and quest["progress"] >= int(quest.get("target", 0)):
                    quest["completed"] = True
                    changed = True
                if award_rewards and quest.get("completed") and not quest.get("claimed"):
                    quest["claimed"] = True
                    reward = int(quest.get("reward", 0))
                    self.coins += reward
                    self.pending_quest_reward += reward
                    if tier == "daily":
                        self.profile_totals["daily_complete"] = int(self.profile_totals.get("daily_complete", 0)) + 1
                    else:
                        self.profile_totals["weekly_complete"] = int(self.profile_totals.get("weekly_complete", 0)) + 1
                    self.add_text(f"QUEST COMPLETE! +{reward}", WIDTH * 0.5, 176, (120, 255, 170))
                    self.queue_notification("QUEST COMPLETE!", quest.get("title", "Quest"), (112, 255, 184), duration=2.8)
                    self.sounds.play("score")
                    changed = True
        for spec in ACHIEVEMENT_SPECS:
            if spec["key"] in self.achievements:
                continue
            value = self.achievement_value(spec["stat"])
            if value >= spec["target"]:
                if self.unlock_achievement(spec["key"]):
                    changed = True
        return changed

    def finish_run(self, result: str):
        if getattr(self, "run_finalized", False):
            return
        self.run_finalized = True
        self.run_stats["result"] = result
        self.run_stats["duration"] = self.time_alive
        self.profile_totals["runs"] = int(self.profile_totals.get("runs", 0)) + 1
        self.profile_totals["max_score"] = max(int(self.profile_totals.get("max_score", 0)), int(self.score))
        self.profile_totals["best_combo"] = max(int(self.profile_totals.get("best_combo", 0)), int(self.combo))
        if result == "CLEAR":
            self.profile_totals["wins"] = int(self.profile_totals.get("wins", 0)) + 1
            if self.boss_mode:
                self.profile_totals["boss_wins"] = int(self.profile_totals.get("boss_wins", 0)) + 1
                if self.current_difficulty().name == "HARD":
                    self.profile_totals["boss_wins_hard"] = int(self.profile_totals.get("boss_wins_hard", 0)) + 1
        elif result == "GAME_OVER":
            self.profile_totals["deaths"] = int(self.profile_totals.get("deaths", 0)) + 1
        reward = 0
        if self.boss_mode:
            if result == "CLEAR":
                reward = self.completion_coin_reward()
        else:
            if result == "GAME_OVER" and self.score >= 30:
                reward = self.completion_coin_reward()
        if reward > 0:
            self.coins += reward
            self.profile_totals["coins_collected"] = int(self.profile_totals.get("coins_collected", 0)) + reward
            self.run_stats["coins_earned"] += reward
        self.evaluate_meta(award_rewards=True)
        self.last_run_summary = {
            "result": result,
            "mode": self.current_mode,
            "difficulty": DIFFICULTIES[self.current_difficulty_index].name,
            "boss": BOSS_SPECS[self.boss_index]["name"] if self.boss_mode else None,
            "score": int(self.score),
            "coins": int(self.run_stats.get("coins_earned", 0)),
            "coins_available": int(self.run_stats.get("coins_available", 0)),
            "time": float(self.time_alive),
            "flaps": int(self.run_stats.get("flaps", 0)),
            "items": int(self.run_stats.get("items_total", 0)),
            "boss_damage": int(self.run_stats.get("boss_damage_dealt", 0)),
            "shield_breaks": int(self.run_stats.get("shield_breaks", 0)),
            "pipes": int(self.run_stats.get("pipes_scored", 0)),
        }
        self.save_settings()

    def profile_back_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH // 2 - 120, HEIGHT - 64, 240, 46)

    def profile_tab_rects(self):
        tab_w = 150
        tab_h = 40
        gap = 10
        total = tab_w * 3 + gap * 2
        start_x = WIDTH // 2 - total // 2
        y = 100
        return {
            "stats": pygame.Rect(start_x, y, tab_w, tab_h),
            "quests": pygame.Rect(start_x + tab_w + gap, y, tab_w, tab_h),
            "achievements": pygame.Rect(start_x + (tab_w + gap) * 2, y, tab_w, tab_h),
        }

    def achievement_card_rect(self, index: int) -> pygame.Rect:
        panel = pygame.Rect(24, 152, WIDTH - 48, 314)
        # Keep the grid compact so the detail strip at the bottom never overlaps.
        grid = pygame.Rect(panel.x + 16, panel.y + 48, panel.width - 32, 198)
        cols = 5
        gap_x = 8
        gap_y = 6
        card_w = (grid.width - gap_x * (cols - 1)) // cols
        card_h = 44
        col = index % cols
        row = index // cols
        x = grid.x + col * (card_w + gap_x)
        y = grid.y + row * (card_h + gap_y)
        return pygame.Rect(x, y, card_w, card_h)

    def draw_achievement_icon(self, icon: str, unlocked: bool) -> pygame.Surface:
        key = (icon, unlocked)
        cache = self.overlay_cache
        # store icons under a separate namespace in overlay_cache to avoid adding another cache.
        if key in cache:
            return cache[key]
        surf = pygame.Surface((72, 72), pygame.SRCALPHA)
        base = (40, 50, 72) if not unlocked else {
            "wing": (255, 220, 140),
            "coin": (255, 200, 90),
            "shield": (110, 220, 255),
            "boss": (255, 110, 140),
            "crown": (245, 210, 100),
            "clock": (120, 205, 255),
            "crate": (160, 180, 210),
            "bolt": (255, 180, 90),
            "quest": (130, 255, 170),
            "star": (255, 230, 150),
            "gem": (180, 140, 255),
            "trophy": (255, 210, 120),
            "medal": (255, 180, 220),
            "run": (120, 240, 200),
        }.get(icon, (200, 200, 220))
        bg = pygame.Surface((72, 72), pygame.SRCALPHA)
        pygame.draw.rect(bg, (*base, 200 if unlocked else 130), (0, 0, 72, 72), border_radius=18)
        pygame.draw.rect(bg, (255, 255, 255, 50 if unlocked else 24), (6, 6, 60, 60), border_radius=15)
        for i in range(6):
            if unlocked:
                pygame.draw.circle(bg, (255, 255, 255, 18), (10 + i * 11, 12 + (i % 3) * 8), 2)
            else:
                pygame.draw.line(bg, (255, 255, 255, 16), (8 + i * 11, 8), (12 + i * 11, 64), 1)
        cx = cy = 36
        fg = (255, 255, 255) if unlocked else (180, 185, 200)
        if icon == "wing":
            pygame.draw.polygon(bg, fg, [(18, 38), (30, 20), (42, 30), (36, 44), (24, 46)])
            pygame.draw.polygon(bg, fg, [(32, 40), (46, 24), (56, 34), (48, 48), (36, 50)])
        elif icon == "coin":
            pygame.draw.circle(bg, fg, (cx, cy), 18, 4)
            pygame.draw.circle(bg, fg, (cx, cy), 10)
        elif icon == "shield":
            pygame.draw.polygon(bg, fg, [(cx, 16), (52, 24), (48, 44), (36, 58), (24, 44), (20, 24)])
        elif icon == "boss":
            pygame.draw.circle(bg, fg, (cx, cy), 18)
            pygame.draw.line(bg, fg, (20, 28), (52, 44), 2)
            pygame.draw.line(bg, fg, (52, 28), (20, 44), 2)
        elif icon == "crown":
            pygame.draw.polygon(bg, fg, [(18, 42), (26, 24), (36, 38), (46, 24), (54, 42), (50, 52), (22, 52)])
        elif icon == "clock":
            pygame.draw.circle(bg, fg, (cx, cy), 18)
            pygame.draw.line(bg, fg, (cx, cy), (cx, 22), 2)
            pygame.draw.line(bg, fg, (cx, cy), (48, 38), 2)
        elif icon == "crate":
            pygame.draw.rect(bg, fg, (18, 22, 36, 28))
            pygame.draw.line(bg, fg, (18, 36), (54, 36), 2)
            pygame.draw.line(bg, fg, (36, 22), (36, 50), 2)
        elif icon == "bolt":
            pygame.draw.polygon(bg, fg, [(34, 14), (22, 40), (34, 40), (30, 58), (50, 30), (38, 30)])
        elif icon == "quest":
            pygame.draw.rect(bg, fg, (18, 18, 36, 40))
            pygame.draw.line(bg, fg, (22, 30), (50, 30), 2)
            pygame.draw.line(bg, fg, (22, 40), (38, 40), 2)
            pygame.draw.line(bg, fg, (22, 48), (44, 48), 2)
        elif icon == "star":
            pts = []
            for i in range(10):
                ang = -math.pi / 2 + i * (math.pi / 5)
                rad = 18 if i % 2 == 0 else 8
                pts.append((cx + int(math.cos(ang) * rad), cy + int(math.sin(ang) * rad)))
            pygame.draw.polygon(bg, fg, pts)
        elif icon == "gem":
            pygame.draw.polygon(bg, fg, [(cx, 14), (52, 30), (cx, 58), (20, 30)])
            pygame.draw.polygon(bg, (255, 255, 255), [(cx, 20), (44, 30), (cx, 50), (28, 30)])
        elif icon == "trophy":
            pygame.draw.rect(bg, fg, (26, 20, 20, 24))
            pygame.draw.arc(bg, fg, (18, 20, 18, 20), 1.2, 4.8, 2)
            pygame.draw.arc(bg, fg, (36, 20, 18, 20), -1.6, 3.0, 2)
            pygame.draw.line(bg, fg, (36, 44), (36, 54), 2)
            pygame.draw.line(bg, fg, (28, 54), (44, 54), 2)
        elif icon == "medal":
            pygame.draw.polygon(bg, fg, [(24, 18), (48, 18), (44, 36), (28, 36)])
            pygame.draw.circle(bg, fg, (cx, 44), 12, 3)
            pygame.draw.line(bg, fg, (30, 52), (24, 62), 2)
            pygame.draw.line(bg, fg, (42, 52), (48, 62), 2)
        elif icon == "run":
            pygame.draw.ellipse(bg, fg, (18, 28, 36, 18))
            pygame.draw.line(bg, fg, (26, 44), (20, 56), 3)
            pygame.draw.line(bg, fg, (40, 44), (48, 56), 3)
        else:
            pygame.draw.circle(bg, fg, (cx, cy), 18)
        surf.blit(bg, (0, 0))
        cache[key] = surf
        return surf

    def draw_run_summary(self, surf: pygame.Surface):
        if not self.last_run_summary:
            return
        lines = [
            f"{self.last_run_summary.get('result', 'RUN').title()}  |  {self.last_run_summary.get('mode', '')}",
            f"Score: {self.last_run_summary.get('score', 0)}   Time: {self.last_run_summary.get('time', 0):.1f}s",
            f"Flaps: {self.last_run_summary.get('flaps', 0)}   Pipes: {self.last_run_summary.get('pipes', 0)}",
            f"Items: {self.last_run_summary.get('items', 0)}   Coins: {self.last_run_summary.get('coins', 0)}",
        ]
        if self.last_run_summary.get('boss'):
            lines.append(f"Boss: {self.last_run_summary.get('boss')}   Core dmg: {self.last_run_summary.get('boss_damage', 0)}")
        if self.last_run_summary.get('shield_breaks', 0):
            lines.append(f"Shield breaks: {self.last_run_summary.get('shield_breaks', 0)}")
        lines = lines[:5]

        boss_result_screen = self.current_mode == "BOSS" and self.state in ("CLEAR", "GAME_OVER")
        if boss_result_screen:
            return

    def draw_profile_screen(self):
        surf = self.screen
        self.draw_background(surf)
        surf.blit(self.get_overlay((WIDTH, HEIGHT), (6, 10, 18, 96)), (0, 0))
        if self.evaluate_meta(award_rewards=True):
            self.save_settings()

        pressed_left = pygame.mouse.get_pressed(num_buttons=3)[0]
        mouse_pos = self._game_mouse_pos()

        draw_text(surf, self.font_huge, "Profile", (WIDTH // 2, 44), WHITE, center=True)
        draw_text(surf, self.font, "Stats - Quests - Achievements", (WIDTH // 2, 84), (220, 230, 240), center=True, shadow=False)

        self._draw_screen_close_btn(surf, self.profile_close_rect())

        tabs = self.profile_tab_rects()
        for key, label, accent in (
            ("stats", "Stats", (255, 220, 140)),
            ("quests", "Quests", (130, 255, 170)),
            ("achievements", "Achievements", (160, 200, 255)),
        ):
            rect = tabs[key]
            active = self.profile_tab == key
            hovered = rect.collidepoint(mouse_pos)
            pressed = hovered and pressed_left
            draw_round_rect(surf, (22, 28, 44), rect, radius=14)
            draw_round_outline(surf, WHITE if (active or pressed or hovered) else (70, 84, 112), rect, radius=14, width=3 if (active or pressed or hovered) else 2)
            self.draw_button_shine(surf, rect, 14)
            self.draw_pulse_overlay(surf, rect, 14, hovered=hovered, active=active, flash=pressed, phase_shift=0.25)
            draw_text(surf, self.font, label, (rect.centerx, rect.centery), WHITE, center=True, shadow=False)

        for d in (-1, 1):
            r = self.profile_nav_rect(d)
            self.draw_nav_arrow(surf, r, d, flash=self.is_button_flashed(r))

        panel = pygame.Rect(24, 152, WIDTH - 48, 314)
        draw_round_rect(surf, (16, 20, 32), panel, radius=22)
        draw_round_rect(surf, (255, 220, 140), panel, radius=22, width=2)

        if self.profile_tab == "stats":
            draw_text(surf, self.font_big, "Player Stats", (panel.centerx, panel.y + 24), WHITE, center=True, shadow=False)
            entries = [
                ("Runs", self.profile_totals["runs"]),
                ("Wins", self.profile_totals["wins"]),
                ("Boss Wins", self.profile_totals["boss_wins"]),
                ("Boss Hard Wins", self.profile_totals["boss_wins_hard"]),
                ("Flaps", self.profile_totals["flaps"]),
                ("Pipes", self.profile_totals["pipes_scored"]),
                ("Coins", self.profile_totals["coins_collected"]),
                ("Items", self.profile_totals["items_total"]),
                ("Play Time", f"{self.profile_totals['play_time']:.0f}s"),
                ("Shield Breaks", self.profile_totals["shield_breaks"]),
                ("Best Score", self.profile_totals["max_score"]),
                ("Best Combo", self.profile_totals["best_combo"]),
                ("Daily Done", self.profile_totals["daily_complete"]),
                ("Weekly Done", self.profile_totals["weekly_complete"]),
                ("Deaths", self.profile_totals["deaths"]),
            ]
            col_x = [panel.x + 36, panel.centerx + 22]
            row_y = panel.y + 72
            line_h = 29
            for i, (label, value) in enumerate(entries):
                col = i % 2
                row = i // 2
                x = col_x[col]
                y = row_y + row * line_h
                draw_text(surf, self.font_small, f"{label}:", (x, y), (220, 230, 240), shadow=False)
                draw_text(surf, self.font_small, str(value), (x + 160, y), WHITE, align="right", shadow=False)

        elif self.profile_tab == "quests":
            draw_text(surf, self.font_big, "Quests", (panel.centerx, panel.y + 24), WHITE, center=True, shadow=False)
            draw_text(surf, self.font_micro, "Daily and weekly contracts", (panel.centerx, panel.y + 46), (182, 194, 210), center=True, shadow=False)
            half_w = (panel.width - 36) // 2
            left_box = pygame.Rect(panel.x + 16, panel.y + 60, half_w, panel.height - 76)
            right_box = pygame.Rect(left_box.right + 4, panel.y + 60, half_w, panel.height - 76)
            for box, tier, title, accent in (
                (left_box, "daily", "Daily", (255, 220, 140)),
                (right_box, "weekly", "Weekly", (160, 200, 255)),
            ):
                draw_round_rect(surf, (20, 26, 40), box, radius=18)
                draw_round_outline(surf, accent, box, radius=18, width=2)
                self.draw_button_shine(surf, box, 18)
                header = pygame.Rect(box.x + 10, box.y + 10, box.width - 20, 30)
                draw_round_rect(surf, (30, 38, 58), header, radius=12)
                draw_round_outline(surf, accent, header, radius=12, width=2)
                draw_text(surf, self.font_small, f"{title} Quests", header.center, accent, center=True, shadow=False)
                for stripe_x in (box.x + 16, box.x + 40, box.x + 64):
                    pygame.draw.line(surf, rgb_lerp(accent, WHITE, 0.22), (stripe_x, box.y + 48), (stripe_x + 24, box.y + 24), 1)
                quests = self.quest_state.get(tier, [])
                qy = box.y + 48
                for quest in quests:
                    if qy + 40 > box.bottom - 10:
                        break
                    progress = int(quest.get("progress", 0))
                    target = int(quest.get("target", 0))
                    reward = int(quest.get("reward", 0))
                    done = bool(quest.get("claimed"))
                    status = "CLAIMED" if done else ("DONE" if quest.get("completed") else f"{progress}/{target}")
                    line = pygame.Rect(box.x + 10, qy, box.width - 20, 38)
                    draw_round_rect(surf, (28, 34, 52), line, radius=12)
                    draw_round_outline(surf, rgb_lerp(accent, (255, 255, 255), 0.30), line, radius=12, width=1)
                    self.draw_button_shine(surf, line, 12)
                    bar = pygame.Rect(line.x + 1, line.y + 1, 6, line.height - 2)
                    draw_round_rect(surf, accent, bar, radius=6)
                    draw_text(surf, self.font_small, quest.get("title", "Quest"), (line.x + 12, line.y + 5), WHITE, shadow=False)
                    draw_text(surf, self.font_micro, status, (line.right - 10, line.y + 5), (120, 255, 170) if done else (255, 220, 140), align="right", shadow=False)
                    draw_text(surf, self.font_micro, quest.get("desc", ""), (line.x + 12, line.y + 21), (220, 230, 240), shadow=False)
                    draw_text(surf, self.font_micro, f"+{reward}", (line.right - 10, line.y + 21), (255, 220, 140), align="right", shadow=False)
                    qy += 44

        else:
            draw_text(surf, self.font_big, "Achievements", (panel.centerx, panel.y + 24), WHITE, center=True, shadow=False)
            hovered_spec = None
            selected_spec = None
            selected_index = int(clamp(self.profile_achievement_index, 0, max(0, len(ACHIEVEMENT_SPECS) - 1)))
            for i, spec in enumerate(ACHIEVEMENT_SPECS):
                card = self.achievement_card_rect(i)
                unlocked = spec["key"] in self.achievements
                hovered = card.collidepoint(mouse_pos)
                pressed = hovered and pressed_left
                selected = i == selected_index
                fill = (31, 40, 60) if (hovered or pressed or selected) else (22, 28, 44)
                edge = WHITE if (hovered or pressed or selected) else ((255, 220, 140) if unlocked else (80, 95, 130))
                draw_round_rect(surf, fill, card, radius=12)
                draw_round_outline(surf, edge, card, radius=12, width=3 if (hovered or pressed or selected) else 2)
                self.draw_button_shine(surf, card, 12)
                if hovered or selected:
                    draw_round_flash(surf, card, 12, 34 if (pressed or selected) else 18)
                top_band = pygame.Rect(card.x + 2, card.y + 2, card.width - 4, 6)
                draw_round_rect(surf, rgb_lerp(edge, (255, 255, 255), 0.28), top_band, radius=4)
                for stripe_x in (card.x + 8, card.x + 28):
                    pygame.draw.line(surf, rgb_lerp(edge, WHITE, 0.18), (stripe_x, card.y + 8), (stripe_x + 10, card.bottom - 8), 1)

                icon_size = 18
                icon = pygame.transform.smoothscale(self.draw_achievement_icon(spec["icon"], unlocked), (icon_size, icon_size))
                icon_y = card.y + (card.height - icon_size) // 2
                surf.blit(icon, (card.x + 7, icon_y))

                value = self.achievement_value(spec["stat"])
                progress_text = f"{int(min(value, spec['target']))}/{spec['target']}"
                title_color = WHITE if unlocked or selected or hovered else (214, 220, 232)
                progress_color = (120, 255, 170) if unlocked else (255, 220, 140)
                draw_text(surf, self.font_small, spec["name"], (card.x + 30, card.y + 5), title_color, shadow=False)
                draw_text(surf, self.font_micro, progress_text, (card.right - 7, card.y + 5), progress_color, align="right", shadow=False)
                draw_text(surf, self.font_micro, sentence_case(spec["desc"]), (card.x + 30, card.y + 22), (205, 214, 226), shadow=False)

                if hovered:
                    hovered_spec = spec
                if selected:
                    selected_spec = spec

            detail = pygame.Rect(panel.x + 16, panel.bottom - 60, panel.width - 32, 50)
            draw_round_rect(surf, (18, 24, 38), detail, radius=16)
            draw_round_outline(surf, (255, 220, 140), detail, radius=16, width=2)
            self.draw_button_shine(surf, detail, 16)
            display_spec = hovered_spec or selected_spec
            flavor_map = {
                "wing": "The sky likes rhythm more than speed.",
                "coin": "Tiny glints can still change a run.",
                "shield": "Staying alive is a skill too.",
                "boss": "Every boss down is a storm survived.",
                "crown": "A clean win always looks royal.",
                "clock": "Time in the air becomes muscle memory.",
                "crate": "Supplies quietly decide comebacks.",
                "bolt": "Fast choices can carry a whole run.",
                "quest": "Side goals build main-story legends.",
                "star": "Small sparks still leave a mark.",
                "gem": "Rare badges deserve rare attention.",
                "trophy": "Proof that the flight was worth it.",
                "medal": "A neat sign of steady progress.",
                "run": "One more run is often the right move.",
            }
            if display_spec is not None:
                unlocked = display_spec['key'] in self.achievements
                progress_value = self.achievement_value(display_spec["stat"])
                progress_text = f"{int(min(progress_value, display_spec['target']))}/{display_spec['target']}"
                state_text = f"{'Unlocked' if unlocked else 'Locked'}  •  {progress_text}"
                flavor_text = flavor_map.get(display_spec["icon"], "A small badge from a bigger sky.")
                icon = pygame.transform.smoothscale(self.draw_achievement_icon(display_spec["icon"], unlocked), (26, 26))
                surf.blit(icon, (detail.x + 12, detail.y + 12))
                draw_text(surf, self.font_small, display_spec["name"], (detail.x + 48, detail.y + 6), WHITE, shadow=False)
                draw_text(surf, self.font_micro, flavor_text, (detail.x + 48, detail.y + 24), (220, 230, 240), shadow=False)
                draw_text(surf, self.font_micro, state_text, (detail.right - 14, detail.y + 6), (120, 255, 170) if unlocked else (255, 220, 140), align="right", shadow=False)
            else:
                draw_text(surf, self.font_small, "Hover or click a card", (detail.x + 48, detail.y + 7), WHITE, shadow=False)
                draw_text(surf, self.font_micro, "A little sky note will appear here.", (detail.x + 48, detail.y + 24), (220, 230, 240), shadow=False)

    def handle_profile_event(self, event):
        back = self.profile_back_rect()
        tabs = self.profile_tab_rects()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.state = "MENU"
                self.save_settings()
            elif event.key == pygame.K_SPACE:
                self.evaluate_meta(award_rewards=True)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                order = ["stats", "quests", "achievements"]
                idx = order.index(self.profile_tab)
                self.profile_tab = order[(idx - 1) % len(order)]
                self.sounds.play("click")
                self.trigger_button_flash(tabs[self.profile_tab])
                self.save_settings()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                order = ["stats", "quests", "achievements"]
                idx = order.index(self.profile_tab)
                self.profile_tab = order[(idx + 1) % len(order)]
                self.sounds.play("click")
                self.trigger_button_flash(tabs[self.profile_tab])
                self.save_settings()
            elif event.key == pygame.K_1:
                self.profile_tab = "stats"
                self.save_settings()
            elif event.key == pygame.K_2:
                self.profile_tab = "quests"
                self.save_settings()
            elif event.key == pygame.K_3:
                self.profile_tab = "achievements"
                self.save_settings()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = self.profile_close_rect()
            if close_rect.collidepoint(event.pos):
                self.trigger_button_flash(close_rect)
                self.sounds.play("click")
                self.state = "MENU"
                self.save_settings()
                return
            order = ["stats", "quests", "achievements"]
            prev_r = self.profile_nav_rect(-1)
            next_r = self.profile_nav_rect(1)
            if prev_r.collidepoint(event.pos):
                idx = order.index(self.profile_tab)
                self.profile_tab = order[(idx - 1) % len(order)]
                self.sounds.play("click")
                self.trigger_button_flash(prev_r)
                self.save_settings()
                return
            if next_r.collidepoint(event.pos):
                idx = order.index(self.profile_tab)
                self.profile_tab = order[(idx + 1) % len(order)]
                self.sounds.play("click")
                self.trigger_button_flash(next_r)
                self.save_settings()
                return
            for key, rect in tabs.items():
                if rect.collidepoint(event.pos):
                    self.profile_tab = key
                    self.trigger_button_flash(rect)
                    self.sounds.play("click")
                    self.save_settings()
                    return
            if self.profile_tab == "achievements":
                for i in range(len(ACHIEVEMENT_SPECS)):
                    card = self.achievement_card_rect(i)
                    if card.collidepoint(event.pos):
                        self.profile_achievement_index = i
                        self.trigger_button_flash(card)
                        self.sounds.play("click")
                        self.save_settings()
                        return
            if back.collidepoint(event.pos):
                self.trigger_button_flash(back)
                self.state = "MENU"
                self.save_settings()

    def reset_world(self):
        self.theme_index = 0
        self.time_alive = 0.0
        self.score = 0
        self.combo = 0
        self.spawn_timer = 0.0
        self.pipe_interval = DIFFICULTIES[self.current_difficulty_index].pipe_interval
        self.pipes: List[Pipe] = []
        self.particles: List[Particle] = []
        self.texts: List[FloatingText] = []
        self.orbs: List[Orb] = []
        self.projectiles: List[BossProjectile] = []
        self.clouds: List[Cloud] = []
        self.wind_phase = 0.0
        self.bird = Bird(230, HEIGHT * 0.48, skin_index=self.skin_index)
        self.mode_clear = False
        self.game_over = False
        self.boss: Optional[Boss] = None
        self.boss_mode = False
        self.boss_intro = 0.0
        self.boss_intro_done = True
        self.boss_entry_fade = 0.0
        self.boss_entry_fade_total = 0.0
        self.boss_hit_flash = 0.0
        self.boss_timer = 0.0
        self.boss_clear_pending = False
        self.boss_clear_timer = 0.0
        self.boss_clear_duration = 2.6
        self.ambient_timer = 0.0
        self.time_scale = 1.0
        self.screen_shake = 0.0
        self.flash = 0.0
        self.active_effects = {"magnet": 0.0, "boost": 0.0, "multiplier": 0.0}
        self.button_fx = []
        self.hold_to_restart = 0.0
        self.run_finalized = False
        self.run_stats = {
            "flaps": 0,
            "pipes_scored": 0,
            "coins_earned": 0,
            "coins_available": 0,
            "items_total": 0,
            "shield_breaks": 0,
            "boss_damage_dealt": 0,
            "item_counts": {},
            "result": "",
            "duration": 0.0,
        }
        # Track last pipe gap center to avoid dead-end corridors between pipes
        self.last_pipe_gap_y = int(HEIGHT * 0.48)
        # ── Boss environmental effect state ───────────────────────────────────
        self.env_flash = 0.0               # 0-1 env-flash intensity
        self.env_flash_color = (255, 255, 255)
        self.env_darkness = 0.0            # 0-1 screen darkness from env
        self.env_event_timer = random.uniform(3.0, 6.0)  # seconds to next env event
        self.env_lightning_bolts: List[List[Tuple]] = []  # each bolt = list of (x,y) points
        self.env_lightning_timer = 0.0     # seconds lightning stays visible
        self.env_ambient_particles: List[Particle] = []   # env-specific particles
        # ─────────────────────────────────────────────────────────────────────
        # ── Boss phase visual effects ─────────────────────────────────────────
        self.boss_ripples: List[dict] = []
        self.boss_afterimages: List[dict] = []
        self._boss_prev_y: float = HEIGHT * 0.44
        self._boss_y_dir: int = 0
        self._boss_afterimage_timer: float = 0.0
        # ── Bird phase visual effects (mirrors boss, gated on boss.phase) ────
        self.bird_ripples: List[dict] = []
        self.bird_afterimages: List[dict] = []
        self._bird_prev_y: float = HEIGHT * 0.48
        self._bird_y_dir: int = 0
        self._bird_afterimage_timer: float = 0.0
        # ─────────────────────────────────────────────────────────────────────
        for i in range(7):
            self.clouds.append(Cloud(random.uniform(0, WIDTH), random.uniform(40, 260), random.uniform(0.6, 1.4), random.uniform(8, 22), i % 3))

    def start_game(self, mode: str, difficulty_index: int, boss_index: Optional[int] = None):
        self.current_mode = mode
        self.current_difficulty_index = difficulty_index
        self.difficulty_cursor = difficulty_index
        if mode == "BOSS":
            if boss_index is None:
                boss_index = self.boss_index
            self.boss_index = boss_index % len(BOSS_SPECS)
        self.reset_world()
        self.state = "PLAY"
        self.message = ""
        self.message_timer = 0.0
        self.last_run_summary = {}
        if mode == "BOSS":
            self.boss_mode = True
            insane_push = 1.08 if DIFFICULTIES[difficulty_index].name == "INSANE" else 1.0
            if BOSS_SPECS[self.boss_index]["name"] == "HELL":
                hp = 100
            else:
                hp = int(round(DIFFICULTIES[difficulty_index].boss_hp * BOSS_SPECS[self.boss_index]["hp_mult"] * 0.92 * insane_push))
            self.boss = Boss(hp=hp, max_hp=hp, boss_id=self.boss_index)
            self.boss_intro = 1.2
            self.boss_intro_done = False
            # Fade from black → clear, finishing just before the first pipe arrives.
            _diff = DIFFICULTIES[difficulty_index]
            _boss_scale = 0.84 if _diff.name == "INSANE" else 0.90
            self.boss_entry_fade_total = max(0.0, _diff.pipe_interval * _boss_scale - 0.15)
            self.boss_entry_fade = self.boss_entry_fade_total
            self.message = ""
            self.message_timer = 0.0
            self.run_stats["boss_name"] = BOSS_SPECS[self.boss_index]["name"]
            self.sounds.play("boss")
        else:
            self.boss_mode = False
        self.ensure_quest_state()
        self.evaluate_meta(award_rewards=False)
        self.save_settings()

    def current_difficulty(self) -> Difficulty:
        return DIFFICULTIES[self.current_difficulty_index]

    def current_theme(self) -> dict:
        if self.boss_mode:
            return BOSS_THEMES[self.boss_index % len(BOSS_THEMES)]
        return THEMES[self.theme_index % len(THEMES)]

    def completion_coin_reward(self) -> int:
        """Return the bonus completion reward, separate from coins collected in the run."""
        difficulty_name = self.current_difficulty().name
        arcade_rewards = {"EASY": 30, "NORMAL": 40, "HARD": 50, "INSANE": 60}
        boss_base_rewards = {"EASY": 50, "NORMAL": 60, "HARD": 80, "INSANE": 120}
        boss_step_rewards = {"EASY": 1, "NORMAL": 1, "HARD": 2, "INSANE": 2}

        if not self.boss_mode:
            return int(arcade_rewards.get(difficulty_name, 40))

        boss_spec = BOSS_SPECS[self.boss_index % len(BOSS_SPECS)]
        if boss_spec.get("name") == "HELL":
            return 500

        base = int(boss_base_rewards.get(difficulty_name, 60))
        step = int(boss_step_rewards.get(difficulty_name, 1))
        return base + (int(self.boss_index) * step)

    def update_theme_by_score(self):
        if self.boss_mode:
            return
        self.theme_index = (self.score // 5) % len(THEMES)

    def update_effects(self, dt: float):
        for key in self.active_effects:
            self.active_effects[key] = max(0.0, self.active_effects[key] - dt)

    def begin_boss_death(self):
        if not (self.boss_mode and self.boss):
            return
        if self.boss_clear_pending:
            return
        self.boss_clear_pending = True
        self.boss_clear_timer = 0.0
        self.boss_clear_duration = 2.6
        self.boss.start_death(self.boss_clear_duration)
        self.boss_intro = 0.0
        self.message = ""
        self.message_timer = max(self.message_timer, self.boss_clear_duration)
        self.projectiles.clear()
        self.orbs.clear()
        self.spawn_timer = 0.0
        self.sounds.play("win")

    def finalize_boss_clear(self):
        if not self.boss_clear_pending:
            return
        self.boss_clear_pending = False
        self.mode_clear = True
        self.state = "CLEAR"
        self.set_best_score(self.score)
        self.coins += 200
        self.profile_totals["coins_collected"] = int(self.profile_totals.get("coins_collected", 0)) + 200
        self.run_stats["coins_earned"] += 200
        self.finish_run("CLEAR")
        self.save_settings()

    def update_button_fx(self, dt: float):
        self.ui_time += dt
        self.button_fx = [(r, t - dt) for (r, t) in self.button_fx if t - dt > 0]

    def trigger_button_flash(self, rect: pygame.Rect):
        self.button_fx.append((rect.copy(), 0.16))

    def is_button_flashed(self, rect: pygame.Rect) -> bool:
        return any(r == rect for r, t in self.button_fx)

    def is_button_hovered(self, rect: pygame.Rect) -> bool:
        return rect.collidepoint(self._game_mouse_pos())

    def draw_button_shine(self, surf: pygame.Surface, rect: pygame.Rect, radius: int):
        cycle = 5.0
        sweep = 0.8
        phase = self.ui_time % cycle
        if phase > sweep:
            return

        progress = phase / sweep
        w, h = rect.size
        pad = max(10, int(min(w, h) * 0.10))

        # Slim, bright diagonal sheen with a premium look.
        shine_w = max(24, int(min(w, h) * 0.22))
        shine = get_clear_surface((w + shine_w * 2, h + shine_w * 2), ("button_shine", w, h, radius))
        center_x = shine.get_width() * 0.50 + int((progress - 0.5) * (w * 1.38))

        for dx in range(-shine_w, shine_w + 1):
            dist = abs(dx) / float(shine_w)
            if dist > 1:
                continue
            alpha = int(220 * (1 - dist) ** 1.85)
            x = int(center_x + dx)
            pygame.draw.line(shine, (255, 255, 255, alpha), (x, 0), (x - int(h * 0.46), shine.get_height()), 1)

        core_w = max(4, shine_w // 6)
        core = get_clear_surface(shine.get_size(), ("button_shine_core", w, h, radius))
        for dx in range(-core_w, core_w + 1):
            dist = abs(dx) / float(core_w)
            alpha = int(255 * (1 - dist) ** 1.25)
            x = int(center_x + dx)
            pygame.draw.line(core, (255, 255, 255, alpha), (x, 0), (x - int(h * 0.46), core.get_height()), 1)
        shine.blit(core, (0, 0))

        shine = pygame.transform.rotate(shine, -24)

        clip = get_clear_surface(rect.size, ("button_shine_clip", rect.size, radius))
        pygame.draw.rect(clip, (255, 255, 255, 255), clip.get_rect(), border_radius=radius)
        temp = get_clear_surface(rect.size, ("button_shine_temp", rect.size, radius))
        temp.blit(shine, (-shine.get_width() // 2 + pad, -shine.get_height() // 2))
        temp.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        glow = get_clear_surface(rect.size, ("button_shine_glow", rect.size, radius))
        glow_rect = pygame.Rect(-int(w * 0.14), int(h * 0.22), int(w * 1.28), max(6, int(h * 0.12)))
        pygame.draw.rect(glow, (255, 255, 255, 18), glow_rect, border_radius=max(2, glow_rect.height // 2))
        glow = pygame.transform.rotate(glow, -24)
        temp.blit(glow, (0, 0))

        surf.blit(temp, rect.topleft)

    def draw_pulse_overlay(self, surf: pygame.Surface, rect: pygame.Rect, radius: int, *, hovered: bool = False, active: bool = False, flash: bool = False, phase_shift: float = 0.0):
        pulse = 0.5 + 0.5 * math.sin(self.ui_time * 3.0 + rect.x * 0.021 + rect.y * 0.017 + phase_shift)
        base = 6 + int(pulse * 8)
        if hovered:
            base += 10
        if active:
            base += 10
        if flash:
            base += 18
        if base <= 0:
            return
        overlay = get_clear_surface(rect.size, ("pulse_overlay", rect.size, radius))
        pygame.draw.rect(overlay, (255, 255, 255, min(72, base)), overlay.get_rect(), border_radius=radius)
        surf.blit(overlay, rect.topleft)

    def menu_item_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(WIDTH // 2 - 170, 188 + index * 58, 340, 48)

    def play_card_rect(self, index: int) -> pygame.Rect:
        card_w = 248
        card_h = 248
        gap = 28
        total = card_w * 3 + gap * 2
        start_x = WIDTH // 2 - total // 2
        y = 188
        return pygame.Rect(start_x + index * (card_w + gap), y, card_w, card_h)
    def play_back_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH // 2 - 110, HEIGHT - 66, 220, 42)

    def difficulty_rect(self, index: int) -> pygame.Rect:
        cols = 2
        card_w = 330
        card_h = 128
        gap_x = 24
        gap_y = 22
        start_x = (WIDTH - (cols * card_w + gap_x)) // 2
        start_y = 166
        col = index % cols
        row = index // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        return pygame.Rect(x, y, card_w, card_h)

    def option_panel_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH // 2 - 312, 76, 624, 404)

    def option_close_rect(self) -> pygame.Rect:
        panel = self.option_panel_rect()
        return pygame.Rect(panel.right - 50, panel.y + 16, 34, 34)

    def skin_close_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH - 54, 14, 34, 34)

    def difficulty_close_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH - 54, 14, 34, 34)

    def boss_select_close_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH - 54, 14, 34, 34)

    def profile_close_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH - 54, 14, 34, 34)

    def _draw_screen_close_btn(self, surf: pygame.Surface, close_rect: pygame.Rect):
        """Draw a red X close button (used on full-screen menus)."""
        hovered = self.is_button_hovered(close_rect)
        close_flash = self.is_button_flashed(close_rect)
        fill = (102, 30, 34) if (hovered or close_flash) else (68, 22, 26)
        edge = (255, 96, 96) if (hovered or close_flash) else (182, 64, 72)
        draw_round_rect(surf, fill, close_rect, radius=11)
        draw_round_outline(surf, edge, close_rect, radius=11, width=2)
        self.draw_button_shine(surf, close_rect, 11)
        self.draw_pulse_overlay(surf, close_rect, 11, hovered=hovered, flash=close_flash, phase_shift=0.7)
        x_font = get_cached_sysfont("arial", 18, bold=True)
        x_img = render_text_cached(x_font, "X", WHITE)
        surf.blit(x_img, x_img.get_rect(center=close_rect.center))

    def option_rect(self, index: int) -> pygame.Rect:
        panel = self.option_panel_rect()
        return pygame.Rect(panel.x + 44, panel.y + 88 + index * 74, panel.width - 88, 66)

    def option_reset_rect(self) -> pygame.Rect:
        panel = self.option_panel_rect()
        return pygame.Rect(panel.centerx - 100, panel.bottom - 58, 200, 44)

    def option_target_rect(self, index: int) -> pygame.Rect:
        if index < len(self.option_items()):
            return self.option_rect(index)
        return self.option_reset_rect()

    def skin_card_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH // 2 - 244, 126, 488, 300)

    def skin_nav_rect(self, direction: int) -> pygame.Rect:
        card = self.skin_card_rect()
        size = 64
        gap = 18
        x = card.left - size - gap if direction < 0 else card.right + gap
        return pygame.Rect(x, card.centery - size // 2, size, size)

    def boss_select_rect(self, index: int) -> pygame.Rect:
        cols = 4
        card_w = 196
        card_h = 86
        gap_x = 14
        gap_y = 12
        total_w = cols * card_w + (cols - 1) * gap_x
        start_x = (WIDTH - total_w) // 2
        start_y = 132
        col = index % cols
        row = index // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        return pygame.Rect(x, y, card_w, card_h)

    def difficulty_nav_rect(self, direction: int) -> pygame.Rect:
        card_h = 128; gap_y = 22
        nrows = (len(DIFFICULTIES) + 1) // 2
        grid_h = nrows * card_h + (nrows - 1) * gap_y
        cy = 166 + grid_h // 2
        aw, ah = 52, 64
        x = 36 if direction < 0 else WIDTH - 36 - aw
        return pygame.Rect(x, cy - ah // 2, aw, ah)

    def boss_nav_rect(self, direction: int) -> pygame.Rect:
        visible = VISIBLE_BOSS_INDICES
        nrows = (len(visible) + 3) // 4
        card_h = 86; gap_y = 12; start_y = 120
        grid_h = nrows * card_h + (nrows - 1) * gap_y
        cy = start_y + grid_h // 2
        aw, ah = 40, 52
        x = 16 if direction < 0 else WIDTH - 16 - aw
        return pygame.Rect(x, cy - ah // 2, aw, ah)

    def profile_nav_rect(self, direction: int) -> pygame.Rect:
        tab_w = 150; tab_h = 40; gap = 10; y = 102
        total = tab_w * 3 + gap * 2
        start_x = WIDTH // 2 - total // 2
        aw, ah = 48, 42
        if direction < 0:
            x = start_x - aw - 12
        else:
            x = start_x + total + 12
        return pygame.Rect(x, y, aw, ah)

    def options_nav_rect(self, direction: int) -> pygame.Rect:
        panel = self.option_panel_rect()
        aw, ah = 54, 42
        cx = panel.centerx
        if direction < 0:
            return pygame.Rect(cx - aw // 2, panel.y - ah - 6, aw, ah)
        else:
            return pygame.Rect(cx - aw // 2, panel.bottom + 6, aw, ah)

    def play_mode_nav_rect(self, direction: int) -> pygame.Rect:
        card_w = 248; gap = 28; n = 3
        total = card_w * n + gap * (n - 1)
        start_x = WIDTH // 2 - total // 2
        cy = 188 + 248 // 2
        aw, ah = 50, 64
        if direction < 0:
            x = start_x - aw - 12
        else:
            x = start_x + total + 12
        return pygame.Rect(x, cy - ah // 2, aw, ah)
    def game_over_button_rect(self, kind: str) -> pygame.Rect:
        if kind == "REPLAY":
            return pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 88, 160, 44)
        return pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 88, 160, 44)

    def clear_button_rect(self, kind: str) -> pygame.Rect:
        if kind == "MENU":
            return pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 88, 160, 44)
        return pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 88, 160, 44)

    def pause_button_rect(self, kind: str) -> pygame.Rect:
        # Centered 3-button layout for the pause menu.
        y = HEIGHT // 2 + 84
        w, h = 156, 46
        gap = 16
        total = w * 3 + gap * 2
        left = WIDTH // 2 - total // 2
        mapping = {
            "RESUME": left,
            "REPLAY": left + w + gap,
            "MENU": left + (w + gap) * 2,
        }
        return pygame.Rect(mapping.get(kind, left), y, w, h)


    def pause_toggle_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH - 72, 14, 52, 36)

    def draw_pause_toggle_button(self, surf: pygame.Surface):
        rect = self.pause_toggle_rect()
        paused = self.state == "PAUSE"
        hovered = self.is_button_hovered(rect)
        active = hovered or paused

        fill = (32, 44, 68) if active else (20, 28, 44)
        edge = WHITE if active else (65, 85, 120)
        draw_round_rect(surf, fill, rect, radius=14)
        draw_round_outline(surf, edge, rect, radius=14, width=3 if active else 2)
        self.draw_button_shine(surf, rect, 14)
        draw_round_flash(surf, rect, 14, 10 if not active else 16)
        if hovered:
            draw_round_flash(surf, rect, 14, 20)
        if self.is_button_flashed(rect):
            draw_round_flash(surf, rect, 14, 62)

        icon = get_clear_surface(rect.size, ("pause_icon", rect.size, paused, active))
        cx, cy = rect.width // 2, rect.height // 2
        icon_color = WHITE if active else (225, 234, 242)
        if paused:
            pts = [(cx - 6, cy - 9), (cx - 6, cy + 9), (cx + 10, cy)]
            pygame.draw.polygon(icon, icon_color, pts)
        else:
            bar_w = 5
            bar_h = 18
            gap = 6
            left_bar = pygame.Rect(cx - gap - bar_w, cy - bar_h // 2, bar_w, bar_h)
            right_bar = pygame.Rect(cx + gap, cy - bar_h // 2, bar_w, bar_h)
            pygame.draw.rect(icon, icon_color, left_bar, border_radius=2)
            pygame.draw.rect(icon, icon_color, right_bar, border_radius=2)
        surf.blit(icon, rect.topleft)

    def click_pause_toggle_button(self, pos) -> bool:
        rect = self.pause_toggle_rect()
        if rect.collidepoint(pos):
            self.trigger_button_flash(rect)
            self.state = "PLAY" if self.state == "PAUSE" else "PAUSE"
            return True
        return False

    def draw_button(self, surf: pygame.Surface, rect: pygame.Rect, label: str, *, active: bool = False, flash: bool = False, font: Optional[pygame.font.Font] = None, accent: Tuple[int, int, int] = (255, 220, 140)):
        if font is None:
            font = self.font
        hovered = self.is_button_hovered(rect)
        fill = (32, 44, 68) if (active or hovered) else (20, 28, 44)
        edge = WHITE if (active or hovered) else (65, 85, 120)
        draw_round_rect(surf, fill, rect, radius=18)
        draw_round_outline(surf, edge, rect, radius=18, width=3 if (active or hovered) else 2)
        self.draw_button_shine(surf, rect, 18)
        draw_round_flash(surf, rect, 18, 10 if not active else 16)
        if hovered:
            draw_round_flash(surf, rect, 18, 20)
        if flash:
            draw_round_flash(surf, rect, 18, 62)
        if label:
            draw_text(surf, font, label, rect.center, WHITE if (active or hovered) else (220, 230, 240), center=True, shadow=False)

    def option_items(self):
        return [
            {
                "title": "Sound",
                "value": "ON" if self.sound_on else "OFF",
                "subtitle": "Toggle audio immediately",
                "icon": "sound_on" if self.sound_on else "sound_off",
                "accent": (120, 255, 170) if self.sound_on else (255, 132, 120),
            },
            {
                "title": "Best Score",
                "value": str(self.current_best_score()),
                "subtitle": "Saved record",
                "icon": "best",
                "accent": (255, 220, 140),
            },
            {
                "title": "Coin",
                "value": str(self.coins),
                "subtitle": "Current wallet",
                "icon": "coin",
                "accent": (255, 208, 96),
            },
        ]

    def draw_option_icon(self, kind: str, accent: Tuple[int, int, int], *, active: bool = False) -> pygame.Surface:
        key = ("option_icon", kind, accent, active)
        cache = self.overlay_cache
        if key in cache:
            return cache[key]

        surf = pygame.Surface((44, 44), pygame.SRCALPHA)
        fg = WHITE if active else (232, 238, 246)

        if kind in ("sound_on", "sound_off"):
            pygame.draw.polygon(surf, fg, [(8, 20), (16, 20), (24, 13), (24, 31), (16, 24), (8, 24)])
            pygame.draw.rect(surf, fg, (8, 20, 8, 4), border_radius=2)
            if kind == "sound_on":
                pygame.draw.arc(surf, accent, (18, 12, 16, 20), -0.85, 0.85, 3)
                pygame.draw.arc(surf, accent, (18, 6, 24, 32), -0.85, 0.85, 3)
            else:
                pygame.draw.line(surf, accent, (29, 13), (39, 31), 4)
                pygame.draw.line(surf, accent, (39, 13), (29, 31), 4)
        elif kind == "best":
            pygame.draw.rect(surf, fg, (13, 10, 18, 14), border_radius=4)
            pygame.draw.arc(surf, accent, (8, 10, 14, 14), 1.2, 5.0, 2)
            pygame.draw.arc(surf, accent, (22, 10, 14, 14), -1.9, 2.0, 2)
            pygame.draw.line(surf, fg, (22, 24), (22, 32), 3)
            pygame.draw.line(surf, accent, (15, 34), (29, 34), 3)
            pygame.draw.circle(surf, accent, (34, 12), 4)
        else:  # coin
            pygame.draw.circle(surf, accent, (22, 22), 14)
            pygame.draw.circle(surf, fg, (22, 22), 11, 3)
            pygame.draw.circle(surf, fg, (22, 22), 4)
            pygame.draw.circle(surf, (255, 255, 255, 120), (17, 17), 3)

        cache[key] = surf
        return surf

    def draw_option_card(self, surf: pygame.Surface, rect: pygame.Rect, item: dict, *, active: bool = False, flash: bool = False):
        hovered = self.is_button_hovered(rect)
        accent = item["accent"]
        fill = (30, 40, 60) if (active or hovered) else (18, 24, 40)
        edge = WHITE if (active or hovered) else rgb_lerp(accent, (86, 104, 136), 0.58)

        draw_round_rect(surf, fill, rect, radius=22)
        draw_round_outline(surf, edge, rect, radius=22, width=3 if (active or hovered) else 2)
        self.draw_button_shine(surf, rect, 22)
        self.draw_pulse_overlay(surf, rect, 22, hovered=hovered, active=active, flash=flash, phase_shift=0.2)

        icon_box = pygame.Rect(rect.x + 14, rect.y + 8, 50, 50)
        draw_round_rect(surf, (*accent, 46), icon_box, radius=16)
        draw_round_outline(surf, accent, icon_box, radius=16, width=2)
        icon = self.draw_option_icon(item["icon"], accent, active=active)
        surf.blit(icon, icon.get_rect(center=icon_box.center))

        title_color = WHITE if active else (224, 232, 242)
        subtitle_color = (196, 208, 222) if active else (172, 184, 202)
        draw_text(surf, self.font, item["title"], (rect.x + 82, rect.y + 10), title_color, shadow=False)
        draw_text(surf, self.font_small, item["subtitle"], (rect.x + 82, rect.y + 38), subtitle_color, shadow=False)

        value_rect = pygame.Rect(rect.right - 126, rect.y + 14, 102, 36)
        draw_round_rect(surf, (*accent, 44), value_rect, radius=14)
        draw_round_outline(surf, accent, value_rect, radius=14, width=2)
        value_font = self.font_big if len(item["value"]) <= 3 else self.font
        draw_text(surf, value_font, item["value"], value_rect.center, WHITE, center=True, shadow=False)

    def draw_skin_nav_button(self, surf: pygame.Surface, rect: pygame.Rect, direction: int, accent: Tuple[int, int, int], *, flash: bool = False):
        hovered = self.is_button_hovered(rect)
        fill = (32, 44, 68) if hovered else (20, 28, 44)
        edge = WHITE if hovered else (65, 85, 120)

        draw_round_rect(surf, fill, rect, radius=22)
        draw_round_outline(surf, edge, rect, radius=22, width=2)
        self.draw_button_shine(surf, rect, 22)
        self.draw_pulse_overlay(surf, rect, 22, hovered=hovered, flash=flash, phase_shift=0.45)

        cx, cy = rect.center
        wing = 12
        reach = 9
        if direction < 0:
            points = [(cx + reach // 2, cy - wing), (cx - reach, cy), (cx + reach // 2, cy + wing)]
        else:
            points = [(cx - reach // 2, cy - wing), (cx + reach, cy), (cx - reach // 2, cy + wing)]
        pygame.draw.lines(surf, WHITE, False, points, 5)

    def draw_nav_arrow(self, surf: pygame.Surface, rect: pygame.Rect, direction: int, *,
                       vertical: bool = False, flash: bool = False,
                       accent: Tuple[int, int, int] = (255, 220, 140)):
        hovered = self.is_button_hovered(rect)
        fill = (32, 44, 68) if hovered else (20, 28, 44)
        draw_round_rect(surf, fill, rect, radius=16)
        draw_round_outline(surf, WHITE if hovered else (65, 85, 120), rect, radius=16, width=2)
        self.draw_button_shine(surf, rect, 16)
        self.draw_pulse_overlay(surf, rect, 16, hovered=hovered, flash=flash, phase_shift=0.33)
        cx, cy = rect.center
        wing = min(10, rect.height // 3)
        reach = min(8, rect.width // 3)
        if not vertical:
            if direction < 0:
                pts = [(cx + reach // 2, cy - wing), (cx - reach, cy), (cx + reach // 2, cy + wing)]
            else:
                pts = [(cx - reach // 2, cy - wing), (cx + reach, cy), (cx - reach // 2, cy + wing)]
        else:
            if direction < 0:
                pts = [(cx - wing, cy + reach // 2), (cx, cy - reach), (cx + wing, cy + reach // 2)]
            else:
                pts = [(cx - wing, cy - reach // 2), (cx, cy + reach), (cx + wing, cy - reach // 2)]
        pygame.draw.lines(surf, WHITE, False, pts, 4)

    def cycle_skin(self, direction: int):
        direction = -1 if direction < 0 else 1
        self.skin_cursor = (self.skin_cursor + direction) % len(SKINS)
        self.sounds.play("click")
        self.trigger_button_flash(self.skin_nav_rect(direction))

    def activate_skin_card(self):
        skin = SKINS[self.skin_cursor]
        card = self.skin_card_rect()
        self.trigger_button_flash(card)
        if self.skin_cursor in self.unlocked:
            self.skin_index = self.skin_cursor
            self.selected_skin = self.skin_index
            self.message = f"Equipped {skin.name.title()}"
            self.message_timer = 1.0
            self.sounds.play("click")
            self.save_settings()
        elif self.coins >= skin.cost:
            self.coins -= skin.cost
            self.unlocked.add(self.skin_cursor)
            self.skin_index = self.skin_cursor
            self.selected_skin = self.skin_index
            self.message = f"Unlocked {skin.name.title()}"
            self.message_timer = 1.0
            self.sounds.play("win")
            self.save_settings()
        else:
            self.message = "Not Enough Coin"
            self.message_timer = 1.0
            self.sounds.play("hit")

    def draw_play_card(self, surf: pygame.Surface, rect: pygame.Rect, kind: str, *, active: bool = False, flash: bool = False):
        hovered = self.is_button_hovered(rect)
        fill = (26, 34, 52) if active else (18, 24, 38)
        edge_map = {"ARCADE": (255, 220, 140), "BOSS": (120, 220, 255), "HELL": (255, 124, 72)}
        title_map = {"ARCADE": "Arcade Mode", "BOSS": "Boss Mode", "HELL": "HELL"}
        edge = WHITE if active else edge_map.get(kind, (180, 180, 180))
        draw_round_rect(surf, fill, rect, radius=26)
        draw_round_outline(surf, edge, rect, radius=26, width=3 if (active or hovered) else 2)
        self.draw_button_shine(surf, rect, 26)
        self.draw_pulse_overlay(surf, rect, 26, hovered=hovered, active=active, flash=flash, phase_shift=0.18)

        inner = rect.inflate(-18, -54)
        preview = get_clear_surface(inner.size, ("play_card_preview", kind, inner.size))
        t = self.menu_scroll
        if kind == "ARCADE":
            pygame.draw.rect(preview, (34, 76, 140), preview.get_rect(), border_radius=20)
            for i in range(3):
                x = 34 + i * 72 + int(math.sin(t * 2.0 + i) * 8)
                gap_y = 58 + (i % 2) * 14
                pygame.draw.rect(preview, (70, 180, 86), (x, 0, 22, gap_y), border_radius=6)
                pygame.draw.rect(preview, (34, 108, 52), (x, gap_y + 48, 22, inner.height - gap_y - 48), border_radius=6)
                pygame.draw.rect(preview, (92, 214, 112), (x - 4, gap_y - 8, 30, 16), border_radius=7)
            bird_x = 60 + int(math.sin(t * 3.2) * 10)
            bird_y = 88 + int(math.sin(t * 4.4) * 5)
            pygame.draw.ellipse(preview, (250, 220, 88), (bird_x, bird_y, 34, 24))
            pygame.draw.ellipse(preview, (232, 168, 42), (bird_x + 8, bird_y + 5, 18, 13))
            pygame.draw.polygon(preview, (255, 164, 42), [(bird_x + 28, bird_y + 10), (bird_x + 38, bird_y + 14), (bird_x + 28, bird_y + 18)])
            pygame.draw.circle(preview, (255, 255, 255), (bird_x + 24, bird_y + 8), 3)
            pygame.draw.circle(preview, (20, 20, 25), (bird_x + 25, bird_y + 8), 1)
            pygame.draw.line(preview, (255, 245, 200), (bird_x + 16, bird_y + 28), (bird_x + 10, bird_y + 36), 2)
            pygame.draw.line(preview, (255, 245, 200), (bird_x + 22, bird_y + 28), (bird_x + 20, bird_y + 38), 2)
        elif kind == "BOSS":
            pygame.draw.rect(preview, (26, 24, 48), preview.get_rect(), border_radius=20)
            for i in range(4):
                x = 34 + i * 52 + int(math.sin(t * 2.6 + i) * 5)
                pygame.draw.rect(preview, (70, 174, 90), (x, 22, 16, 92), border_radius=6)
                pygame.draw.rect(preview, (34, 108, 52), (x, 114, 16, 58), border_radius=6)
                pygame.draw.rect(preview, (92, 224, 112), (x - 3, 18, 22, 12), border_radius=6)
            for i in range(7):
                yy = 34 + i * 18 + int(math.sin(t * 3.2 + i) * 4)
                pygame.draw.line(preview, (255, 220, 255, 70), (16, yy), (inner.width - 44, yy + 10), 2)
            bird_x = 58 + int(math.sin(t * 3.0) * 8)
            bird_y = 90 + int(math.sin(t * 4.0) * 4)
            pygame.draw.ellipse(preview, (250, 220, 88), (bird_x, bird_y, 34, 24))
            pygame.draw.ellipse(preview, (232, 168, 42), (bird_x + 8, bird_y + 5, 18, 13))
            pygame.draw.polygon(preview, (255, 164, 42), [(bird_x + 28, bird_y + 10), (bird_x + 38, bird_y + 14), (bird_x + 28, bird_y + 18)])
            pygame.draw.circle(preview, (255, 255, 255), (bird_x + 24, bird_y + 8), 3)
            pygame.draw.circle(preview, (20, 20, 25), (bird_x + 25, bird_y + 8), 1)
            boss_x = inner.width - 72
            boss_y = 24 + int(math.sin(t * 2.5) * 4)
            pygame.draw.circle(preview, (130, 80, 180), (boss_x, boss_y + 26), 28)
            pygame.draw.circle(preview, (255, 216, 255), (boss_x, boss_y + 26), 14)
            eye_offset = int(math.sin(t * 4.0) * 2)
            pygame.draw.polygon(preview, (255, 216, 255), [(boss_x - 18 + eye_offset, boss_y + 8), (boss_x - 6 + eye_offset, boss_y + 18), (boss_x - 18 + eye_offset, boss_y + 28)])
            pygame.draw.polygon(preview, (255, 216, 255), [(boss_x + 18 + eye_offset, boss_y + 8), (boss_x + 6 + eye_offset, boss_y + 18), (boss_x + 18 + eye_offset, boss_y + 28)])
            wing_flap = int(math.sin(t * 5.0) * 3)
            for i in range(5):
                sx = 124 + i * 16
                sy = 44 + i * 10 + wing_flap
                pygame.draw.circle(preview, (255, 122, 172), (sx, sy), 3)
            for i in range(4):
                pygame.draw.line(preview, (255, 122, 172), (114 + i * 28, 80 + wing_flap), (146 + i * 28, 56 - wing_flap), 2)
        else:
            pygame.draw.rect(preview, (48, 12, 12), preview.get_rect(), border_radius=20)
            for i in range(5):
                x = 24 + i * 40 + int(math.sin(t * 3.0 + i) * 8)
                height = 64 + (i % 2) * 26
                pygame.draw.rect(preview, (250, 96, 28), (x, 18, 18, height), border_radius=6)
                pygame.draw.rect(preview, (155, 32, 14), (x, 18 + height, 18, inner.height - 18 - height), border_radius=6)
                pygame.draw.rect(preview, (255, 220, 140), (x - 4, 16, 26, 12), border_radius=6)
            for i in range(8):
                yy = 34 + i * 18 + int(math.sin(t * 3.4 + i) * 5)
                pygame.draw.line(preview, (255, 220, 120, 90), (12, yy), (inner.width - 28, yy + 10), 2)
            for i in range(3):
                px = 30 + i * 52 + int(math.sin(t * 4.0 + i) * 8)
                py = 118 - i * 10 + int(math.cos(t * 3.6 + i) * 4)
                pygame.draw.circle(preview, (255, 124, 72), (px, py), 2)
                pygame.draw.circle(preview, (255, 220, 140), (px, py), 5, 1)
            bird_x = 52 + int(math.sin(t * 3.4) * 8)
            bird_y = 88 + int(math.sin(t * 4.6) * 6)
            pygame.draw.ellipse(preview, (255, 226, 104), (bird_x, bird_y, 34, 24))
            pygame.draw.ellipse(preview, (255, 138, 48), (bird_x + 8, bird_y + 5, 18, 13))
            pygame.draw.polygon(preview, (255, 198, 72), [(bird_x + 28, bird_y + 10), (bird_x + 38, bird_y + 14), (bird_x + 28, bird_y + 18)])
            pygame.draw.circle(preview, (255, 255, 255), (bird_x + 24, bird_y + 8), 3)
            pygame.draw.circle(preview, (20, 20, 25), (bird_x + 25, bird_y + 8), 1)
            boss_x = inner.width - 74
            boss_y = 22 + int(math.sin(t * 2.4) * 5)
            pygame.draw.circle(preview, (255, 92, 40), (boss_x, boss_y + 28), 30)
            pygame.draw.circle(preview, (255, 220, 140), (boss_x, boss_y + 28), 16)
            for i in range(6):
                ang = t * 2.5 + i * (math.tau / 6)
                px = boss_x + int(math.cos(ang) * 46)
                py = boss_y + 28 + int(math.sin(ang) * 36)
                pygame.draw.line(preview, (255, 124, 72), (boss_x, boss_y + 28), (px, py), 2)
            pygame.draw.polygon(preview, (255, 220, 140), [(boss_x - 18, boss_y + 8), (boss_x - 4, boss_y + 18), (boss_x - 18, boss_y + 28)])
            pygame.draw.polygon(preview, (255, 220, 140), [(boss_x + 18, boss_y + 8), (boss_x + 4, boss_y + 18), (boss_x + 18, boss_y + 28)])

        surf.blit(preview, inner.topleft)
        draw_text(surf, self.font_big, title_map.get(kind, kind.title()), (rect.centerx, rect.bottom - 24), edge, center=True, shadow=False)
    def item_multiplier(self) -> int:
        return 2 if self.active_effects["multiplier"] > 0 else 1

    def add_particle(self, x, y, vx, vy, life, size, color, gravity=0.0):
        if len(self.particles) < 240:
            self.particles.append(Particle(x, y, vx, vy, life, size, color, gravity))

    def add_burst(self, x, y, base_color, amount=10, speed=180):
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            spd = random.uniform(speed * 0.35, speed)
            self.add_particle(
                x, y,
                math.cos(angle) * spd,
                math.sin(angle) * spd - 60,
                random.uniform(0.35, 0.8),
                random.uniform(2, 5),
                base_color,
                gravity=420.0,
            )

    def add_text(self, text, x, y, color=WHITE):
        if len(self.texts) < 20:
            self.texts.append(FloatingText(str(text).upper(), x, y, -24, 1.0, color))

    def queue_notification(self, title: str, subtitle: str = "", color: Tuple[int, int, int] = (255, 220, 140), *, duration: float = 2.8):
        if not hasattr(self, "notifications"):
            self.notifications = []
        self.notifications.append({
            "title": str(title).strip(),
            "subtitle": str(subtitle),
            "color": color,
            "life": float(duration),
            "duration": float(duration),
        })
        if len(self.notifications) > 8:
            self.notifications = self.notifications[-8:]

    def update_notifications(self, dt: float):
        if not hasattr(self, "notifications"):
            self.notifications = []
            return
        for note in self.notifications:
            note["life"] = max(0.0, float(note["life"]) - dt)
        self.notifications = [n for n in self.notifications if n["life"] > 0]

    def draw_notifications(self, surf: pygame.Surface):
        if not getattr(self, "notifications", None):
            return
        font_title = get_cached_sysfont("arial", 19, bold=True)
        font_sub = get_cached_sysfont("arial", 15, bold=True)
        badge_font = get_cached_sysfont("arial", 16, bold=True)
        active = self.notifications[-3:]
        now = pygame.time.get_ticks() * 0.004

        for i, note in enumerate(reversed(active)):
            life = max(0.0, min(1.0, float(note["life"]) / float(note["duration"])))
            alpha = int(255 * (0.20 + 0.80 * ease_out_cubic(life)))
            width = 464
            height = 68 if note["subtitle"] else 52
            x = WIDTH // 2 - width // 2
            y = 14 + i * (height + 8)

            title = str(note["title"]).strip()
            subtitle = str(note["subtitle"]).strip()
            title_upper = title.upper()
            accent = note["color"]
            if "QUEST" in title_upper:
                accent = rgb_lerp(accent, (120, 255, 190), 0.18)
                badge_fill = (28, 96, 64)
                badge_text = "Q"
            elif "ARCHIEVEMENT" in title_upper or "ACHIEVEMENT" in title_upper:
                accent = rgb_lerp(accent, (255, 130, 96), 0.26)
                badge_fill = (96, 34, 30)
                badge_text = "A"
            else:
                badge_fill = rgb_lerp(accent, (40, 46, 60), 0.30)
                badge_text = "!"
            edge = rgb_lerp(accent, WHITE, 0.22)
            fill = (10, 14, 24)
            panel = get_clear_surface((width, height), ("notification_panel", width, height))

            pygame.draw.rect(panel, (*fill, int(220 * (alpha / 255))), (0, 0, width, height), border_radius=20)
            pygame.draw.rect(panel, (*accent, min(255, alpha)), (0, 0, width, height), width=2, border_radius=20)
            pygame.draw.rect(panel, (255, 255, 255, int(14 * (alpha / 255))), (4, 4, width - 8, max(10, height // 4)), border_radius=16)

            stripe = get_clear_surface((width, height), ("notification_stripe", width, height))
            stripe_shift = int((now * 80 + i * 22) % 32)
            for sx in range(-40, width + 40, 20):
                x1 = sx + stripe_shift
                pygame.draw.line(stripe, (*accent, int(18 * (alpha / 255))), (x1, 0), (x1 - 36, height), 2)
            panel.blit(stripe, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            if "QUEST" in title.upper() or "ACHIEVEMENT" in title.upper() or "ARCHIEVEMENT" in title.upper():
                top_band = pygame.Rect(8, 8, width - 16, 14)
                pygame.draw.rect(panel, (*accent, int(95 * (alpha / 255))), top_band, border_radius=7)
                pygame.draw.rect(panel, (255, 255, 255, int(42 * (alpha / 255))), top_band, width=1, border_radius=7)

            badge = pygame.Rect(12, height // 2 - 16, 32, 32)
            pygame.draw.rect(panel, (*badge_fill, min(255, alpha)), badge, border_radius=12)
            pygame.draw.rect(panel, (*edge, min(255, alpha)), badge, width=2, border_radius=12)
            badge_label = render_text_cached(badge_font, badge_text, WHITE)
            badge_label.set_alpha(alpha)
            panel.blit(badge_label, badge_label.get_rect(center=badge.center))

            title_img = render_text_cached(font_title, title, WHITE).copy()
            title_img.set_alpha(alpha)
            panel.blit(title_img, title_img.get_rect(topleft=(56, 10)))
            if subtitle:
                subtitle_img = render_text_cached(font_sub, subtitle, WHITE).copy()
                subtitle_img.set_alpha(alpha)
                panel.blit(subtitle_img, subtitle_img.get_rect(topleft=(56, 34)))

            glow = get_clear_surface((width, height), ("notification_glow", width, height))
            pygame.draw.circle(glow, (*accent, int(48 * (alpha / 255))), (width - 42, height // 2), 28)
            panel.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            surf.blit(panel, (x, y))

    def spawn_item_fx(self, kind: str, x: float, y: float, collected: bool = True):
        color = {
            "shield": (100, 230, 255),
            "coin": (255, 220, 100),
            "magnet": (255, 120, 120),
            "boost": (160, 255, 180),
            "multiplier": (255, 175, 255),
            "revive": (255, 210, 120),
            "core": (255, 150, 90),
        }.get(kind, WHITE)
        amount = 8 if kind == "coin" else 10 if kind in ("shield", "magnet", "boost", "revive") else 12
        speed = 110 if collected else 140
        if kind == "core":
            amount = 14
            speed = 155
        self.add_burst(x, y, color, amount=amount, speed=speed)
        if kind == "coin":
            self.add_burst(x, y, (255, 245, 180), amount=6, speed=80)
            for ang in np.linspace(0, math.tau, 6, endpoint=False):
                self.add_particle(x + math.cos(ang) * 6, y + math.sin(ang) * 6, math.cos(ang) * 35, math.sin(ang) * 35, 0.2, 1.6, (255, 240, 160))
        elif kind == "magnet":
            for ang in np.linspace(0, math.tau, 8, endpoint=False):
                self.add_particle(x + math.cos(ang) * 7, y + math.sin(ang) * 7, math.cos(ang) * 55, math.sin(ang) * 55, 0.28, 2, (255, 140, 140))
            self.add_burst(x, y, (255, 170, 170), amount=4, speed=70)
            for ang in np.linspace(0, math.tau, 6, endpoint=False):
                self.add_particle(x + math.cos(ang) * 14, y + math.sin(ang) * 14, math.cos(ang) * 18, math.sin(ang) * 18, 0.18, 1.4, (255, 220, 220))
        elif kind == "boost":
            for _ in range(10):
                self.add_particle(x - random.uniform(4, 10), y + random.uniform(-8, 8), random.uniform(-220, -120), random.uniform(-30, 30), 0.22, random.uniform(1.5, 2.5), (185, 255, 205), gravity=0.0)
            self.add_burst(x, y, (170, 255, 195), amount=6, speed=110)
        elif kind == "multiplier":
            for ang in np.linspace(0, math.tau, 10, endpoint=False):
                self.add_particle(x + math.cos(ang) * 8, y + math.sin(ang) * 8, math.cos(ang) * 45, math.sin(ang) * 45, 0.26, 2, (255, 210, 255))
            self.add_burst(x, y, (255, 210, 255), amount=6, speed=100)
        elif kind == "shield":
            self.add_burst(x, y, (180, 245, 255), amount=8, speed=120)
            for ang in np.linspace(0, math.tau, 6, endpoint=False):
                self.add_particle(x + math.cos(ang) * 7, y + math.sin(ang) * 7, math.cos(ang) * 60, math.sin(ang) * 60, 0.24, 2, (100, 230, 255))
        elif kind == "revive":
            self.add_burst(x, y, (255, 242, 210), amount=10, speed=155)
            for ang in np.linspace(0, math.tau, 8, endpoint=False):
                self.add_particle(x + math.cos(ang) * 6, y + math.sin(ang) * 6, math.cos(ang) * 70, math.sin(ang) * 70, 0.26, 2.2, (255, 210, 120))
            self.screen_shake = max(self.screen_shake, 0.08)
        elif kind == "core":
            self.add_burst(x, y, (255, 185, 120), amount=16, speed=175)
            self.add_burst(x, y, (255, 255, 255), amount=6, speed=80)
            for _ in range(5):
                self.add_particle(x, y, random.uniform(-60, 60), random.uniform(-120, -40), 0.22, 2, (255, 140, 90), gravity=120.0)
        for angle in (0, math.pi / 2):
            dx = math.cos(angle) * 10
            dy = math.sin(angle) * 10
            self.add_particle(x + dx, y + dy, dx * 2.0, dy * 2.0, 0.18, 2, color)

    def spawn_item_use_fx(self, kind: str, x: float, y: float):
        color = {
            "shield": (100, 230, 255),
            "coin": (255, 220, 100),
            "magnet": (255, 120, 120),
            "boost": (160, 255, 180),
            "multiplier": (255, 175, 255),
            "revive": (255, 210, 120),
            "core": (255, 150, 90),
        }.get(kind, WHITE)
        self.add_burst(x, y, color, amount=10 if kind != "core" else 16, speed=180 if kind != "core" else 220)

        if kind == "shield":
            self.screen_shake = max(self.screen_shake, 0.12)
            self.flash = max(self.flash, 0.08)
            for ang in np.linspace(0, math.tau, 12, endpoint=False):
                self.add_particle(
                    x + math.cos(ang) * 8,
                    y + math.sin(ang) * 8,
                    math.cos(ang) * 150,
                    math.sin(ang) * 150,
                    0.30,
                    2.3,
                    (180, 245, 255),
                    gravity=0.0,
                )
            self.add_burst(x, y, (180, 245, 255), amount=6, speed=90)
            for ang in np.linspace(0, math.tau, 6, endpoint=False):
                self.add_particle(x + math.cos(ang) * 16, y + math.sin(ang) * 16, math.cos(ang) * 26, math.sin(ang) * 26, 0.22, 1.6, (255, 255, 255), gravity=0.0)
        elif kind == "boost":
            self.screen_shake = max(self.screen_shake, 0.05)
            for _ in range(12):
                self.add_particle(x - random.uniform(8, 18), y + random.uniform(-10, 10), random.uniform(-260, -140), random.uniform(-18, 18), 0.24, random.uniform(1.5, 2.4), (185, 255, 205), gravity=0.0)
            self.add_burst(x, y, (255, 255, 255), amount=4, speed=70)
        elif kind == "magnet":
            for ang in np.linspace(0, math.tau, 14, endpoint=False):
                self.add_particle(x + math.cos(ang) * 6, y + math.sin(ang) * 6, math.cos(ang) * 60, math.sin(ang) * 60, 0.24, 2, (255, 135, 135))
            self.add_burst(x, y, (255, 255, 255), amount=6, speed=85)
        elif kind == "multiplier":
            self.flash = max(self.flash, 0.06)
            for ang in np.linspace(0, math.tau, 10, endpoint=False):
                self.add_particle(x + math.cos(ang) * 7, y + math.sin(ang) * 7, math.cos(ang) * 95, math.sin(ang) * 95, 0.24, 2, (255, 210, 255))
            self.add_burst(x, y, (255, 210, 255), amount=5, speed=110)
            self.add_text("X2", x, y - 18, (255, 210, 255))
        elif kind == "revive":
            self.screen_shake = max(self.screen_shake, 0.16)
            self.flash = max(self.flash, 0.12)
            self.add_burst(x, y, (255, 240, 200), amount=22, speed=260)
            for ang in np.linspace(0, math.tau, 18, endpoint=False):
                self.add_particle(
                    x + math.cos(ang) * 6,
                    y + math.sin(ang) * 6,
                    math.cos(ang) * 190,
                    math.sin(ang) * 190 - 30,
                    0.34,
                    2.6,
                    (255, 225, 140),
                    gravity=0.0,
                )
            self.add_text("REVIVE", x, y - 18, (255, 220, 140))
        elif kind == "core":
            self.screen_shake = max(self.screen_shake, 0.10)
            self.flash = max(self.flash, 0.10)
            self.add_burst(x, y, (255, 170, 90), amount=20, speed=220)
            for _ in range(10):
                self.add_particle(x, y, random.uniform(-70, 70), random.uniform(-170, -60), 0.22, 2, (255, 140, 90), gravity=120.0)
        elif kind == "coin":
            self.add_burst(x, y, (255, 245, 180), amount=6, speed=95)
        else:
            self.add_burst(x, y, color, amount=4, speed=120)

    def spawn_shield_break_fx(self, x: float, y: float):
        shield_color = (100, 230, 255)
        for i in range(16):
            angle = i * (math.tau / 16)
            vx = math.cos(angle) * random.uniform(110, 220)
            vy = math.sin(angle) * random.uniform(110, 220)
            self.add_particle(x, y, vx, vy, random.uniform(0.22, 0.5), random.uniform(2, 4), shield_color, gravity=250.0)
        self.add_burst(x, y, shield_color, amount=18, speed=250)

    def spawn_skin_trail_fx(self, x: float, y: float, skin: Skin, strong: bool = False):
        name = skin.fx
        amount = 5 if not strong else 8
        if name == "EMBER":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-140, -30), random.uniform(-120, 20), random.uniform(0.25, 0.5), random.uniform(2, 4), random.choice([(255, 110, 60), (255, 155, 60), (255, 210, 120)]), gravity=260.0)
        elif name == "AQUA" or name == "MINT" or name == "GHOST":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-120, -20), random.uniform(-50, 50), random.uniform(0.32, 0.7), random.uniform(2, 4), random.choice([skin.accent, skin.trail, (240, 255, 255)]), gravity=60.0)
        elif name == "SHADOW" or name == "VOID":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-110, -40), random.uniform(-40, 40), random.uniform(0.35, 0.65), random.uniform(2, 4), random.choice([(80, 85, 110), skin.accent, (35, 40, 55)]), gravity=80.0)
        elif name == "PIXEL":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-130, -25), random.uniform(-90, 30), random.uniform(0.25, 0.48), random.uniform(3, 5), random.choice([(255, 194, 96), (255, 128, 88), (90, 255, 190)]), gravity=180.0)
        elif name == "LAGOON":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-140, -20), random.uniform(-40, 40), random.uniform(0.28, 0.6), random.uniform(2, 4), random.choice([(124, 228, 255), (92, 230, 210), (72, 170, 255)]), gravity=70.0)
                if random.random() < 0.35:
                    self.add_particle(x + random.uniform(-6, 6), y + random.uniform(-6, 6), random.uniform(-40, 40), random.uniform(-30, 30), 0.22, 2, (255, 255, 255), gravity=0.0)
        elif name == "LAVA":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-150, -30), random.uniform(-120, 25), random.uniform(0.25, 0.48), random.uniform(2, 4), random.choice([(255, 130, 64), (255, 90, 48), (255, 190, 120)]), gravity=300.0)
        elif name == "PRISM":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-145, -20), random.uniform(-70, 70), random.uniform(0.28, 0.55), random.uniform(2, 4), random.choice([(255, 200, 255), (120, 255, 255), (255, 130, 220)]), gravity=90.0)
        elif name == "CYBER":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-135, -25), random.uniform(-80, 25), random.uniform(0.22, 0.46), random.uniform(2, 4), random.choice([(95, 245, 255), (255, 95, 190), (28, 160, 255)]), gravity=40.0)
                if random.random() < 0.3:
                    self.add_particle(x, y, random.uniform(-30, 30), random.uniform(-20, 20), 0.15, 1.5, (255, 255, 255), gravity=0.0)
        elif name == "FROST":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-125, -20), random.uniform(-20, 40), random.uniform(0.32, 0.68), random.uniform(2, 4), random.choice([(232, 248, 255), (170, 240, 255), (100, 220, 255)]), gravity=30.0)
        elif name == "GALAXY":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-120, -15), random.uniform(-50, 50), random.uniform(0.25, 0.55), random.uniform(2, 4), random.choice([(190, 160, 255), (255, 120, 220), (130, 110, 255)]), gravity=110.0)
        elif name == "SAND":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-120, -20), random.uniform(-20, 25), random.uniform(0.25, 0.5), random.uniform(2, 4), random.choice([(255, 235, 160), (220, 190, 110), (190, 145, 70)]), gravity=180.0)
        elif name == "ROSE":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-130, -25), random.uniform(-75, 35), random.uniform(0.25, 0.55), random.uniform(2, 4), random.choice([(255, 170, 190), (255, 145, 180), (120, 255, 170)]), gravity=95.0)
        elif name == "STEEL":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-115, -20), random.uniform(-35, 30), random.uniform(0.3, 0.6), random.uniform(2, 4), random.choice([(186, 198, 220), (96, 108, 130), (120, 210, 255)]), gravity=150.0)
        elif name == "CORAL":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-140, -25), random.uniform(-95, 30), random.uniform(0.3, 0.58), random.uniform(2, 4), random.choice([(255, 170, 132), (255, 100, 92), (100, 230, 210)]), gravity=120.0)
        elif name == "CHERRY":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-135, -35), random.uniform(-95, 25), random.uniform(0.3, 0.55), random.uniform(2, 4), random.choice([(255, 130, 190), (255, 170, 205), (255, 235, 240)]), gravity=120.0)
        elif name == "ROYAL" or name == "SOLAR" or name == "VIOLET":
            for _ in range(amount):
                self.add_particle(x, y, random.uniform(-145, -30), random.uniform(-95, 35), random.uniform(0.25, 0.55), random.uniform(2, 4), random.choice([skin.accent, skin.trail, (255, 255, 255)]), gravity=140.0)
        else:
            self.add_burst(x, y, skin.trail, amount=amount, speed=150 if not strong else 180)

    def apply_item(self, kind: str, x: float, y: float):
        self.run_stats["items_total"] += 1
        self.profile_totals["items_total"] = int(self.profile_totals.get("items_total", 0)) + 1
        counts = self.profile_totals.setdefault("item_counts", {})
        counts[kind] = int(counts.get(kind, 0)) + 1
        self.run_stats.setdefault("item_counts", {})[kind] = int(self.run_stats.get("item_counts", {}).get(kind, 0)) + 1

        if kind == "shield":
            self.bird.shield = 7.0 if self.current_difficulty().name == "EASY" else 6.5 if self.current_difficulty().name == "NORMAL" else 6.0
            self.add_text("SHIELD", self.bird.x, self.bird.y - 24, (100, 230, 255))
            self.spawn_item_use_fx(kind, x, y)
            self.sounds.play("power")
        elif kind == "revive":
            self.bird.revives += 1
            self.add_text("REVIVE +1", self.bird.x, self.bird.y - 24, (255, 210, 120))
            self.spawn_item_use_fx(kind, x, y)
            self.sounds.play("power")
        elif kind == "coin":
            earned = 10 * self.item_multiplier()
            self.coins += earned
            self.profile_totals["coins_collected"] = int(self.profile_totals.get("coins_collected", 0)) + earned
            self.run_stats["coins_earned"] += earned
            self.add_text(f"+{earned} COIN", self.bird.x, self.bird.y - 24, (255, 220, 100))
            self.spawn_item_use_fx(kind, x, y)
            self.sounds.play("score")
        elif kind == "magnet":
            self.active_effects["magnet"] = 5.8 if self.current_difficulty().name == "EASY" else 5.4 if self.current_difficulty().name == "NORMAL" else 5.0
            self.add_text("Magnet", self.bird.x, self.bird.y - 24, (255, 120, 120))
            self.spawn_item_use_fx(kind, x, y)
            self.sounds.play("power")
        elif kind == "boost":
            self.active_effects["boost"] = 5.0 if self.current_difficulty().name == "EASY" else 4.8 if self.current_difficulty().name == "NORMAL" else 4.5
            self.add_text("Boost", self.bird.x, self.bird.y - 24, (160, 255, 180))
            self.spawn_item_use_fx(kind, x, y)
            self.sounds.play("power")
        elif kind == "multiplier":
            self.active_effects["multiplier"] = 6.5 if self.current_difficulty().name == "EASY" else 6.0 if self.current_difficulty().name == "NORMAL" else 5.5
            self.add_text("X2 Bonus", self.bird.x, self.bird.y - 24, (255, 175, 255))
            self.spawn_item_use_fx(kind, x, y)
            self.sounds.play("power")
        elif kind == "core":
            if self.boss_mode and self.boss:
                self.boss.hp -= 1
                self.run_stats["boss_damage_dealt"] += 1
                self.profile_totals["boss_damage_dealt"] = int(self.profile_totals.get("boss_damage_dealt", 0)) + 1
                self.boss_hit_flash = 0.18
                self.screen_shake = max(self.screen_shake, 0.14)
                self.flash = max(self.flash, 0.08)
                self.add_text("-1 BOSS HP", self.bird.x, self.bird.y - 24, (255, 150, 90))
                self.spawn_item_use_fx(kind, x, y)
                self.sounds.play("score")
                if self.boss.hp <= 0:
                    self.begin_boss_death()

    def spawn_pipe(self):
        difficulty = self.current_difficulty()
        gap = difficulty.pipe_gap
        if self.boss_mode and self.boss and self.boss.phase >= 2:
            gap = int(gap * (0.90 if difficulty.name == "INSANE" else 0.93))

        # ── Dead-end prevention ──────────────────────────────────────────────
        # Limit how far the new gap center can jump from the previous pipe so
        # the bird always has a traversable corridor.  HELL and Boss use tighter
        # budgets; Arcade is more generous so it stays fun without feeling railed.
        is_hell = self.boss_mode and self.boss and self.boss.spec().get("short") == "HELL"
        if is_hell:
            max_delta = 80
        elif self.boss_mode:
            max_delta = {"EASY": 150, "NORMAL": 125, "HARD": 105, "INSANE": 88}.get(difficulty.name, 105)
        else:
            max_delta = {"EASY": 200, "NORMAL": 170, "HARD": 148, "INSANE": 128}.get(difficulty.name, 148)

        gap_min = 150
        gap_max = HEIGHT - 130
        lo = int(max(gap_min, self.last_pipe_gap_y - max_delta))
        hi = int(min(gap_max, self.last_pipe_gap_y + max_delta))
        if lo > hi:
            lo, hi = gap_min, gap_max  # safety fallback
        gap_y = random.randint(lo, hi)
        self.last_pipe_gap_y = gap_y
        # ────────────────────────────────────────────────────────────────────
        variant_roll = random.random()
        variant = 0
        move_amp = 0.0
        if not self.boss_mode:
            if difficulty.name == "INSANE":
                if variant_roll < 0.24:
                    variant = 1
                    move_amp = random.uniform(0.55, 1.18)
                elif variant_roll < 0.42:
                    variant = 2
                    move_amp = random.uniform(0.55, 1.30)
            else:
                if variant_roll < 0.18 and self.current_difficulty_index > 0:
                    variant = 1
                    move_amp = random.uniform(0.4, 1.0)
                elif variant_roll < 0.27 and self.current_difficulty_index == 2:
                    variant = 2
                    move_amp = random.uniform(0.4, 1.1)
        pipe = Pipe(WIDTH + 30, gap_y, gap, speed=difficulty.pipe_speed, variant=variant, move_amp=move_amp, theme_index=self.theme_index)
        self.pipes.append(pipe)

        if not self.boss_mode:
            if random.random() < difficulty.power_rate:
                if difficulty.name == "EASY":
                    table = [("coin", 0.25), ("magnet", 0.18), ("boost", 0.17), ("shield", 0.07), ("revive", 0.09), ("multiplier", 0.24)]
                elif difficulty.name == "NORMAL":
                    table = [("coin", 0.26), ("magnet", 0.18), ("boost", 0.17), ("shield", 0.06), ("revive", 0.08), ("multiplier", 0.25)]
                else:
                    table = [("coin", 0.27), ("magnet", 0.18), ("boost", 0.17), ("shield", 0.05), ("revive", 0.07), ("multiplier", 0.26)]
                kinds, weights = zip(*table)
                kind = random.choices(kinds, weights=weights, k=1)[0]
                spread = 42 if difficulty.name == "EASY" else 36 if difficulty.name == "NORMAL" else 32
                orb_y = gap_y + random.randint(-spread, spread)
                self.orbs.append(Orb(pipe.x + pipe.width * 0.5, orb_y, kind, vx=-difficulty.pipe_speed))
                if kind == "coin":
                    self.run_stats["coins_available"] += 10
        elif self.boss:
            boss_drop = boss_item_table(difficulty.name, self.boss.phase)
            boss_short = self.boss.spec().get("short", "")
            if random.random() < boss_drop["drop_rate"]:
                pack_x = pipe.x + pipe.width * 0.5
                if boss_short == "HELL":
                    y = clamp(gap_y + random.randint(-6, 6), 110, HEIGHT - 110)
                    self.orbs.append(Orb(pack_x, y, "core", vx=-difficulty.pipe_speed))
                else:
                    support_kinds, support_weights = zip(*boss_drop["support_table"])
                    pack_size = 1
                    if self.boss.phase >= 2 and random.random() < boss_drop["duo_chance"]:
                        pack_size += 1
                    if self.boss.phase >= 3 and random.random() < boss_drop["trio_chance"]:
                        pack_size += 1

                    y_spread = 16 if self.boss.phase == 1 else 22 if self.boss.phase == 2 else 28
                    x_offsets = {1: [0], 2: [-18, 18], 3: [-28, 0, 28]}[pack_size]

                    for i in range(pack_size):
                        kind = "core" if (i == 0 and random.random() < boss_drop["core_chance"]) else random.choices(support_kinds, weights=support_weights, k=1)[0]
                        y = clamp(gap_y + random.randint(-y_spread, y_spread), 110, HEIGHT - 110)
                        if kind == "core":
                            y = clamp(gap_y + random.randint(-8, 8), 110, HEIGHT - 110)
                        self.orbs.append(Orb(pack_x + x_offsets[i], y, kind, vx=-difficulty.pipe_speed))
                        if kind == "coin":
                            self.run_stats["coins_available"] += 10

    def hit_bird(self):
        if self.bird.shield > 0:
            self.bird.shield = 0.0
            self.bird.invuln = max(self.bird.invuln, 2.0)
            self.screen_shake = 0.22
            self.flash = 0.14
            self.run_stats["shield_breaks"] += 1
            self.profile_totals["shield_breaks"] = int(self.profile_totals.get("shield_breaks", 0)) + 1
            self.spawn_shield_break_fx(self.bird.x, self.bird.y)
            self.add_text("SHIELD BREAK", self.bird.x, self.bird.y - 46, (100, 230, 255))
            self.sounds.play("hit")
            return False
        if self.bird.revives > 0:
            self.bird.revives -= 1
            self.bird.invuln = max(self.bird.invuln, 2.0)
            self.screen_shake = 0.30
            self.flash = 0.18
            self.spawn_item_use_fx("revive", self.bird.x, self.bird.y)
            self.add_text(f"REVIVE LEFT X{self.bird.revives}", self.bird.x, self.bird.y - 46, (255, 210, 120))
            self.sounds.play("power")
            return False
        if self.bird.invuln > 0:
            return False
        self.game_over = True
        self.state = "GAME_OVER"
        self.screen_shake = 0.35
        self.flash = 0.20
        self.sounds.play("hit")
        self.add_burst(self.bird.x, self.bird.y, self.bird.skin().bird_alt, amount=28, speed=300)
        self.finish_run("GAME_OVER")
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Boss environmental effects — update
    # ─────────────────────────────────────────────────────────────────────────
    def _gen_lightning_bolt(self, x1, y1, x2, y2, jitter=28, segments=10):
        """Return a list of (x,y) points for a jagged lightning bolt."""
        pts = [(x1, y1)]
        for i in range(1, segments):
            t = i / segments
            mx = lerp(x1, x2, t) + random.randint(-jitter, jitter)
            my = lerp(y1, y2, t) + random.randint(-jitter // 2, jitter // 2)
            pts.append((mx, my))
        pts.append((x2, y2))
        return pts

    def update_boss_env(self, dt: float):
        """Update per-boss environmental hazard state."""
        if not (self.boss_mode and self.boss and not self.boss.dying):
            return

        spec = self.boss.spec()
        art = spec.get("art", "aegis")
        is_hell = spec.get("name") == "HELL"
        phase = self.boss.phase

        # Decay flashes / darkness
        self.env_flash = max(0.0, self.env_flash - dt * 3.5)
        self.env_darkness = max(0.0, self.env_darkness - dt * 1.2)
        self.env_lightning_timer = max(0.0, self.env_lightning_timer - dt)
        if self.env_lightning_timer <= 0:
            self.env_lightning_bolts.clear()

        # Update ambient env particles
        for p in self.env_ambient_particles:
            p.update(dt)
        retain_positive_life(self.env_ambient_particles)

        # Tick-down to next env event
        self.env_event_timer -= dt
        if self.env_event_timer > 0:
            # Emit continuous ambient particles even between events
            self._emit_env_ambient(art, is_hell, dt)
            return

        # ── Fire an environmental event ──────────────────────────────────────
        self.env_event_timer = random.uniform(
            3.5 - phase * 0.5,
            7.0 - phase * 0.8
        )

        if is_hell or art == "ember":
            # Hellfire / Ember: blinding heat burst + heavy ember rain
            self.env_flash = 0.55 + phase * 0.12
            self.env_flash_color = (255, 120, 40)
            self.screen_shake = max(self.screen_shake, 0.14 + phase * 0.04)
            for _ in range(22 + phase * 6):
                x = random.uniform(0, WIDTH)
                self.env_ambient_particles.append(Particle(
                    x, -12,
                    random.uniform(-20, 20),
                    random.uniform(120, 260),
                    random.uniform(1.0, 2.2),
                    random.uniform(3, 6),
                    random.choice([(255, 100, 30), (255, 160, 50), (255, 220, 90)]),
                    gravity=60.0,
                ))
            if is_hell:
                # HELL: extra darkness + screen-edge hellfire columns
                self.env_darkness = min(1.0, 0.40 + phase * 0.08)
                for _ in range(8 + phase * 2):
                    x = random.choice([random.uniform(0, 80), random.uniform(WIDTH - 80, WIDTH)])
                    self.env_ambient_particles.append(Particle(
                        x, HEIGHT - 20,
                        random.uniform(-30, 30),
                        random.uniform(-280, -160),
                        random.uniform(0.6, 1.2),
                        random.uniform(5, 9),
                        random.choice([(255, 60, 20), (255, 120, 40)]),
                        gravity=-20.0,
                    ))

        elif art == "tempest":
            # Tempest: lightning strike, dark-then-flash, screen shake
            self.env_darkness = min(1.0, 0.45 + phase * 0.10)
            # Brief darkness precedes flash
            self.env_event_timer = max(self.env_event_timer, 0.8)  # strike in 0.8s
            # Schedule the flash at next small tick via storing state
            # Immediately spawn 1-3 lightning bolts
            num_bolts = 1 + (phase >= 2) + (phase >= 3)
            self.env_lightning_bolts.clear()
            for _ in range(num_bolts):
                bx = random.randint(80, WIDTH - 80)
                self.env_lightning_bolts.append(
                    self._gen_lightning_bolt(bx, 0, bx + random.randint(-60, 60), HEIGHT - 80)
                )
            self.env_lightning_timer = 0.18 + phase * 0.04
            self.env_flash = 0.70 + phase * 0.10
            self.env_flash_color = (200, 230, 255)
            self.screen_shake = max(self.screen_shake, 0.22 + phase * 0.06)
            # Wind gusts
            for _ in range(14 + phase * 4):
                self.env_ambient_particles.append(Particle(
                    WIDTH + random.uniform(0, 60),
                    random.uniform(30, HEIGHT - 60),
                    random.uniform(-380, -200),
                    random.uniform(-30, 30),
                    random.uniform(0.3, 0.7),
                    random.uniform(1.5, 3),
                    (200, 230, 255),
                    gravity=0.0,
                ))

        elif art == "void":
            # Void: darkness surge, everything dims, boss glows
            self.env_darkness = min(1.0, 0.55 + phase * 0.12)
            self.env_flash = 0.25
            self.env_flash_color = (80, 30, 140)
            # Purple void-dust particles implode toward boss
            bx, by = self.boss.x, self.boss.y
            for _ in range(16 + phase * 4):
                ang = random.uniform(0, math.tau)
                dist = random.uniform(120, 320)
                px = bx + math.cos(ang) * dist
                py = by + math.sin(ang) * dist
                spd = random.uniform(80, 160)
                self.env_ambient_particles.append(Particle(
                    px, py,
                    math.cos(ang + math.pi) * spd,
                    math.sin(ang + math.pi) * spd,
                    random.uniform(0.5, 1.0),
                    random.uniform(2, 4),
                    random.choice([(160, 80, 255), (100, 40, 200), (200, 140, 255)]),
                    gravity=0.0,
                ))

        elif art == "frost":
            # Frost: blizzard burst + cold tint
            self.env_flash = 0.35
            self.env_flash_color = (200, 230, 255)
            self.env_darkness = min(1.0, 0.25 + phase * 0.08)
            for _ in range(20 + phase * 5):
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH),
                    -8,
                    random.uniform(-60, 60),
                    random.uniform(60, 160),
                    random.uniform(1.2, 2.4),
                    random.uniform(2, 5),
                    random.choice([(230, 248, 255), (190, 230, 255), (255, 255, 255)]),
                    gravity=10.0,
                ))

        elif art == "tide":
            # Tide: wave surge flash + bubble particles
            self.env_flash = 0.40
            self.env_flash_color = (60, 160, 220)
            self.screen_shake = max(self.screen_shake, 0.10 + phase * 0.04)
            for _ in range(16 + phase * 4):
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH),
                    HEIGHT - random.uniform(10, 60),
                    random.uniform(-30, 30),
                    random.uniform(-100, -40),
                    random.uniform(0.8, 1.6),
                    random.uniform(3, 6),
                    random.choice([(80, 200, 255), (120, 220, 255), (200, 240, 255)]),
                    gravity=-20.0,
                ))

        elif art == "chrono":
            # Chrono: time-stutter — brief visual slow + desaturated flash
            self.env_flash = 0.30
            self.env_flash_color = (220, 190, 100)
            self.screen_shake = max(self.screen_shake, 0.08)
            # Gear/clock particles burst from boss
            bx, by = self.boss.x, self.boss.y
            for i in range(12 + phase * 3):
                ang = i * (math.tau / (12 + phase * 3))
                spd = random.uniform(60, 140)
                self.env_ambient_particles.append(Particle(
                    bx, by,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd,
                    random.uniform(0.5, 1.0),
                    random.uniform(2, 4),
                    random.choice([(255, 200, 100), (255, 240, 180), (180, 120, 60)]),
                    gravity=60.0,
                ))

        elif art == "stellar":
            # Stellar: shooting-star sweep + starburst
            self.env_flash = 0.45
            self.env_flash_color = (255, 230, 120)
            for _ in range(5 + phase):
                start_x = random.uniform(0, WIDTH)
                start_y = random.uniform(0, HEIGHT // 3)
                spd = random.uniform(300, 500)
                ang = random.uniform(0.3, 0.8)
                self.env_ambient_particles.append(Particle(
                    start_x, start_y,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd,
                    random.uniform(0.3, 0.6),
                    random.uniform(2, 4),
                    random.choice([(255, 240, 180), (255, 220, 120), (255, 255, 255)]),
                    gravity=0.0,
                ))

        elif art == "nova":
            # Nova: radial supernova flash rings
            self.env_flash = 0.60 + phase * 0.08
            self.env_flash_color = (255, 220, 120)
            self.screen_shake = max(self.screen_shake, 0.12 + phase * 0.04)
            bx, by = self.boss.x, self.boss.y
            for _ in range(18 + phase * 5):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(100, 220)
                self.env_ambient_particles.append(Particle(
                    bx, by,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd,
                    random.uniform(0.4, 0.9),
                    random.uniform(2, 5),
                    random.choice([(255, 220, 120), (255, 180, 60), (255, 255, 200)]),
                    gravity=0.0,
                ))

        elif art == "rift":
            # Rift: dimension-tear — screen glitch shake, purple flash + bolt
            self.env_darkness = min(1.0, 0.50 + phase * 0.10)
            self.env_flash = 0.55
            self.env_flash_color = (120, 60, 255)
            self.screen_shake = max(self.screen_shake, 0.20 + phase * 0.06)
            # Horizontal rift tear bolts
            self.env_lightning_bolts.clear()
            for _ in range(1 + phase):
                ry = random.randint(60, HEIGHT - 80)
                self.env_lightning_bolts.append(
                    self._gen_lightning_bolt(0, ry, WIDTH, ry + random.randint(-20, 20), jitter=16, segments=14)
                )
            self.env_lightning_timer = 0.14 + phase * 0.03

        elif art == "obsidian":
            # Obsidian: shard rain + dark pulse
            self.env_darkness = min(1.0, 0.40 + phase * 0.10)
            self.env_flash = 0.25
            self.env_flash_color = (180, 120, 255)
            for _ in range(14 + phase * 4):
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH),
                    -10,
                    random.uniform(-40, 40),
                    random.uniform(160, 300),
                    random.uniform(0.5, 1.0),
                    random.uniform(3, 6),
                    random.choice([(130, 80, 200), (180, 130, 255), (80, 60, 140)]),
                    gravity=80.0,
                ))

        elif art == "aurora":
            # Aurora: shimmering ribbon wave overlay, gentle colored pulses
            self.env_flash = 0.20
            self.env_flash_color = random.choice([(120, 255, 210), (180, 120, 255), (120, 210, 255)])
            for _ in range(10 + phase * 3):
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH),
                    random.uniform(0, HEIGHT // 2),
                    random.uniform(-40, 40),
                    random.uniform(20, 60),
                    random.uniform(1.5, 3.0),
                    random.uniform(4, 8),
                    random.choice([(132, 255, 232), (160, 120, 255), (120, 255, 180)]),
                    gravity=0.0,
                ))

        elif art in ("thorn", "bloom"):
            # Thorn / Bloom: spore pollen drift + vine tendrils
            self.env_flash = 0.18
            self.env_flash_color = (120, 255, 150)
            for _ in range(16 + phase * 4):
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH),
                    HEIGHT - random.uniform(10, 40),
                    random.uniform(-60, 60),
                    random.uniform(-120, -40),
                    random.uniform(1.5, 3.0),
                    random.uniform(3, 5),
                    random.choice([(100, 220, 120), (160, 255, 140), (200, 255, 180)]),
                    gravity=-10.0,
                ))

        elif art == "prism":
            # Prism: rainbow light beam flash
            self.env_flash = 0.35
            self.env_flash_color = random.choice([(255, 100, 200), (100, 200, 255), (200, 255, 100)])
            for _ in range(12 + phase * 3):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(120, 240)
                bx, by = self.boss.x, self.boss.y
                self.env_ambient_particles.append(Particle(
                    bx, by,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd,
                    random.uniform(0.3, 0.7),
                    random.uniform(2, 5),
                    random.choice([(255, 100, 200), (100, 200, 255), (200, 255, 100), (255, 220, 80)]),
                    gravity=0.0,
                ))

        elif art == "aegis":
            # Aegis: energy-ring pulse, hex-grid flash
            self.env_flash = 0.28
            self.env_flash_color = (180, 200, 255)
            bx, by = self.boss.x, self.boss.y
            for i in range(10 + phase * 2):
                ang = i * (math.tau / (10 + phase * 2))
                spd = random.uniform(80, 160)
                self.env_ambient_particles.append(Particle(
                    bx, by,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd,
                    random.uniform(0.4, 0.9),
                    random.uniform(2, 4),
                    spec["accent"],
                    gravity=0.0,
                ))

        elif art == "sentinel":
            # Sentinel: red scan-line pulse
            self.env_flash = 0.22
            self.env_flash_color = (220, 230, 255)
            for _ in range(8 + phase * 2):
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH),
                    random.uniform(0, HEIGHT),
                    0, 0,
                    random.uniform(0.2, 0.4),
                    random.uniform(1, 2),
                    (220, 230, 255),
                    gravity=0.0,
                ))

        self._emit_env_ambient(art, is_hell, dt)

    def _emit_env_ambient(self, art: str, is_hell: bool, dt: float):
        """Continuously emit low-density ambient particles between events."""
        if len(self.env_ambient_particles) >= 120:
            return
        phase = self.boss.phase if self.boss else 1
        rate = dt * (8 + phase * 2)  # particles-per-second scaled by dt

        if is_hell or art == "ember":
            if random.random() < rate * 0.9:
                x = random.uniform(0, WIDTH)
                self.env_ambient_particles.append(Particle(
                    x, -6,
                    random.uniform(-15, 15),
                    random.uniform(80, 180),
                    random.uniform(0.8, 1.8),
                    random.uniform(2, 4),
                    random.choice([(255, 80, 20), (255, 140, 40)]),
                    gravity=40.0,
                ))
        elif art == "frost":
            if random.random() < rate * 0.7:
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH), -6,
                    random.uniform(-20, 20), random.uniform(30, 80),
                    random.uniform(2.0, 4.0), random.uniform(1.5, 3.5),
                    random.choice([(220, 240, 255), (200, 230, 255)]),
                    gravity=5.0,
                ))
        elif art == "tempest":
            if random.random() < rate * 0.6:
                self.env_ambient_particles.append(Particle(
                    WIDTH + 10, random.uniform(20, HEIGHT - 40),
                    random.uniform(-300, -140), random.uniform(-10, 10),
                    random.uniform(0.2, 0.5), random.uniform(1, 2.5),
                    (190, 220, 255), gravity=0.0,
                ))
        elif art in ("thorn", "bloom"):
            if random.random() < rate * 0.5:
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH), HEIGHT,
                    random.uniform(-30, 30), random.uniform(-50, -20),
                    random.uniform(2.0, 4.0), random.uniform(2, 4),
                    random.choice([(120, 220, 130), (180, 255, 160)]),
                    gravity=-5.0,
                ))
        elif art == "stellar" or art == "nova":
            if random.random() < rate * 0.3:
                self.env_ambient_particles.append(Particle(
                    random.uniform(0, WIDTH), random.uniform(0, HEIGHT // 2),
                    random.uniform(-10, 10), random.uniform(-5, 5),
                    random.uniform(0.8, 1.8), random.uniform(1, 2),
                    (255, 240, 180), gravity=0.0,
                ))

    # ─────────────────────────────────────────────────────────────────────────
    # Boss environmental effects — draw (background layer and foreground)
    # ─────────────────────────────────────────────────────────────────────────
    def draw_boss_env_bg_layer(self, surf: pygame.Surface):
        """Draw env effects that sit between background and game objects."""
        if not (self.boss_mode and self.boss and not self.boss.dying):
            return
        spec = self.boss.spec()
        art = spec.get("art", "aegis")
        is_hell = spec.get("name") == "HELL"
        t = self.time_alive
        phase = self.boss.phase

        # Darkness overlay (dims everything, boss+bullets drawn on top separately)
        if self.env_darkness > 0.02:
            dark_surf = self.get_overlay((WIDTH, HEIGHT), (0, 0, 0, int(self.env_darkness * 200)))
            surf.blit(dark_surf, (0, 0))

        # Tempest/Rift: lightning tint overlay when bolt is active
        if self.env_lightning_timer > 0 and self.env_lightning_bolts:
            bolt_alpha = int(self.env_lightning_timer / 0.22 * 60)
            tint_color = (180, 200, 255) if art == "tempest" else (120, 60, 255)
            surf.blit(self.get_overlay((WIDTH, HEIGHT), (*tint_color, bolt_alpha)), (0, 0))

        # Tide: animated wave overlay at bottom
        if art == "tide":
            wave_surf = get_clear_surface((WIDTH, 80), ("boss_env_wave", art))
            for i in range(4):
                amp = 10 + i * 4
                phase_off = t * 1.8 + i * 0.9
                yy = 40 + int(math.sin(phase_off) * amp)
                pygame.draw.arc(wave_surf, (60, 160, 220, 50 - i * 10),
                    (-20, yy - 30, WIDTH + 40, 60), 0, math.pi, 3)
            surf.blit(wave_surf, (0, HEIGHT - 100))

        # Aurora: ribbon wave layers
        if art == "aurora":
            ribbon = get_clear_surface((WIDTH, HEIGHT // 2), ("boss_env_ribbon", art))
            colors = [(132, 255, 232, 28), (160, 120, 255, 20), (120, 210, 255, 22)]
            for ci, col in enumerate(colors):
                for x in range(0, WIDTH, 8):
                    yy = HEIGHT // 4 + int(math.sin(x * 0.012 + t * 1.1 + ci * 1.8) * (30 + ci * 10))
                    pygame.draw.circle(ribbon, col, (x, yy), 2 + ci)
            surf.blit(ribbon, (0, 0))

        # Frost: icy vignette edges
        if art == "frost":
            frost_alpha = int(30 + 20 * math.sin(t * 0.7))
            frost = get_clear_surface((WIDTH, HEIGHT), ("boss_env_frost", art))
            for edge_size in (60, 40, 20):
                pygame.draw.rect(frost, (210, 235, 255, frost_alpha // (edge_size // 20)),
                    (0, 0, WIDTH, edge_size))
                pygame.draw.rect(frost, (210, 235, 255, frost_alpha // (edge_size // 20)),
                    (0, HEIGHT - edge_size, WIDTH, edge_size))
            surf.blit(frost, (0, 0))

        # Stellar: slow pulsing star-field vignette
        if art == "stellar":
            star_surf = get_clear_surface((WIDTH, HEIGHT), ("boss_env_stars", art))
            for i in range(24):
                sx = (i * 43 + int(t * 15)) % WIDTH
                sy = (i * 71 + int(t * 9)) % (HEIGHT - 40) + 20
                alpha = int(80 + 40 * math.sin(t * 2.0 + i))
                pygame.draw.circle(star_surf, (255, 240, 180, alpha), (sx, sy), 1)
            surf.blit(star_surf, (0, 0))

        # Void: pulsing dark vignette ring
        if art == "void":
            vp = int(20 + 14 * math.sin(t * 1.4))
            vign = get_clear_surface((WIDTH, HEIGHT), ("boss_env_vign", art))
            pygame.draw.ellipse(vign, (30, 10, 60, vp),
                (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
            surf.blit(vign, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def draw_boss_env_fg_layer(self, surf: pygame.Surface):
        """Draw env effects on top of everything (glow overlay, lightning bolts)."""
        if not (self.boss_mode and self.boss):
            return
        spec = self.boss.spec()
        art = spec.get("art", "aegis")
        is_hell = spec.get("name") == "HELL"
        t = self.time_alive

        # Draw ambient env particles
        for p in self.env_ambient_particles:
            p.draw(surf)

        # Lightning bolts
        if self.env_lightning_timer > 0 and self.env_lightning_bolts:
            bolt_alpha = int(clamp(self.env_lightning_timer / 0.22, 0.0, 1.0) * 255)
            bolt_color = (200, 230, 255) if art == "tempest" else (180, 120, 255)
            core_color = (255, 255, 255)
            for bolt in self.env_lightning_bolts:
                for i in range(len(bolt) - 1):
                    p1, p2 = bolt[i], bolt[i + 1]
                    # Glow layer
                    pygame.draw.line(surf, (*bolt_color, bolt_alpha // 3), p1, p2, 5)
                    # Core
                    pygame.draw.line(surf, (*core_color, bolt_alpha), p1, p2, 2)

            # If darkness was applied, re-draw boss and its bullets so they glow
            if self.env_darkness > 0.05 and self.boss and not self.boss.dying:
                self.boss.draw(surf, self.font, self.current_difficulty())
                for proj in self.projectiles:
                    proj.draw(surf)

        # If darkness overlay is active (non-lightning): re-draw boss+bullets so they shine through
        elif self.env_darkness > 0.10 and self.boss and not self.boss.dying:
            self.boss.draw(surf, self.font, self.current_difficulty())
            for proj in self.projectiles:
                proj.draw(surf)

        # Env flash
        if self.env_flash > 0.02:
            r, g, b = self.env_flash_color
            alpha = int(self.env_flash * 140)
            surf.blit(self.get_overlay((WIDTH, HEIGHT), (r, g, b, alpha)), (0, 0))

    def update_play(self, dt: float):
        difficulty = self.current_difficulty()
        self.time_alive += dt
        if self.boss_entry_fade > 0:
            self.boss_entry_fade = max(0.0, self.boss_entry_fade - dt)
        self.wind_phase += dt
        self.profile_totals["play_time"] = float(self.profile_totals.get("play_time", 0.0)) + float(dt)
        self.update_theme_by_score()
        self.update_effects(dt)

        if self.boss_clear_pending and self.boss and self.boss.dying:
            self.boss.update_death(dt)
            self.boss_clear_timer = self.boss.death_timer
            for p in self.particles:
                p.update(dt)
            retain_positive_life(self.particles)
            for t in self.texts:
                t.update(dt)
            retain_positive_life(self.texts)
            for cloud in self.clouds:
                cloud.update(dt * 0.35)
            retain_clouds(self.clouds)
            while len(self.clouds) < 7:
                self.clouds.append(Cloud(WIDTH + random.uniform(0, 160), random.uniform(40, 260), random.uniform(0.6, 1.4), random.uniform(8, 22), random.randint(0, 2)))
            self.ambient_timer += dt
            self.message_timer = max(0.0, self.message_timer - dt)
            self.screen_shake = max(0.0, self.screen_shake - dt)
            self.flash = max(0.0, self.flash - dt)
            self.boss_hit_flash = max(0.0, self.boss_hit_flash - dt)
            if self.boss.death_finished():
                self.finalize_boss_clear()
            if self.evaluate_meta(award_rewards=True):
                self.save_settings()
            return

        gravity_scale = 0.90 if self.active_effects["boost"] > 0 else 1.0
        self.bird.update(dt, difficulty, gravity_scale=gravity_scale)
        if self.bird.y < 0 or self.bird.y > HEIGHT - 40:
            self.hit_bird()

        self.spawn_timer += dt
        spawn_interval = difficulty.pipe_interval
        if self.boss_mode:
            if difficulty.name == "INSANE":
                spawn_interval *= 0.72 if self.boss and self.boss.phase >= 2 else 0.84
            else:
                spawn_interval *= 0.78 if self.boss and self.boss.phase >= 2 else 0.90
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            self.spawn_pipe()

        for cloud in self.clouds:
            cloud.update(dt)
        retain_clouds(self.clouds)
        while len(self.clouds) < 7:
            self.clouds.append(Cloud(WIDTH + random.uniform(0, 160), random.uniform(40, 260), random.uniform(0.6, 1.4), random.uniform(8, 22), random.randint(0, 2)))

        pipe_dt = dt
        for pipe in self.pipes:
            pipe.update(pipe_dt, difficulty, self.score)
        write = 0
        for pipe in self.pipes:
            if pipe.x + pipe.width > -80:
                self.pipes[write] = pipe
                write += 1
        del self.pipes[write:]

        for orb in self.orbs:
            orb.update(pipe_dt)
        retain_active_orbs(self.orbs)

        for proj in self.projectiles:
            proj.update(dt)
        retain_projectiles(self.projectiles)

        for p in self.particles:
            p.update(dt)
        retain_positive_life(self.particles)

        for t in self.texts:
            t.update(dt)
        retain_positive_life(self.texts)

        if self.boss_mode and self.boss:
            self.boss.update(pipe_dt, difficulty, self.pipes, self.projectiles, self.orbs, self.score)
            if self.boss.phase_changed and not self.boss.dying:
                spec = self.boss.spec()
                for _ in range(18 + self.boss.phase * 8):
                    ang = random.uniform(0, math.tau)
                    spd = random.uniform(90, 240) + self.boss.phase * 18
                    self.add_particle(
                        self.boss.x,
                        self.boss.y,
                        math.cos(ang) * spd,
                        math.sin(ang) * spd - random.uniform(30, 90),
                        random.uniform(0.35, 0.95),
                        random.uniform(2.0, 4.6),
                        spec["accent"],
                        gravity=120.0,
                    )
                self.add_burst(self.boss.x, self.boss.y, spec["core"], amount=14 + self.boss.phase * 4, speed=260)
                self.screen_shake = max(self.screen_shake, 0.22 + 0.06 * self.boss.phase)
                self.flash = max(self.flash, 0.10 + 0.02 * self.boss.phase)
                self.boss_hit_flash = max(self.boss_hit_flash, 0.16)
                self.add_text(f"PHASE {self.boss.phase}", self.boss.x, self.boss.y - 92, spec["accent"])
            self.boss.phase_changed = False
            if self.boss_intro > 0:
                self.boss_intro = max(0.0, self.boss_intro - dt)
                if self.boss_intro <= 0:
                    self.boss_intro_done = True

        # Boss environmental hazards
        if self.boss_mode:
            self.update_boss_env(dt)

        self.bird.invuln = max(self.bird.invuln, 0.0)
        if self.bird.boost > 0:
            self.add_particle(self.bird.x - 18, self.bird.y + 4, random.uniform(-140, -50), random.uniform(-30, 30), 0.30, random.uniform(2, 4), self.bird.skin().trail, gravity=100.0)

        # Cache bird rect once for collision checks
        bird_rect = self.bird.rect()
        magnet_on = self.active_effects["magnet"] > 0
        for orb in self.orbs:
            if not orb.active:
                continue
            if magnet_on:
                dx = self.bird.x - orb.x
                dy = self.bird.y - orb.y
                dist2 = dx * dx + dy * dy
                if dist2 < 250 * 250 and dist2 > 1:
                    # Use math.hypot for faster distance calculation
                    dist = math.hypot(dx, dy)
                    strength = clamp(320 + (250 - dist) * 3.4, 160, 560)
                    orb.x += (dx / dist) * strength * dt
                    orb.y += (dy / dist) * strength * dt * 0.92
            if bird_rect.colliderect(orb.rect()):
                orb.active = False
                self.spawn_item_fx(orb.kind, orb.x, orb.y, collected=True)
                self.apply_item(orb.kind, orb.x, orb.y)

        # Reuse cached bird_rect for projectile collision
        if self.bird.invuln <= 0:
            for proj in self.projectiles:
                if bird_rect.colliderect(proj.rect()):
                    if self.hit_bird():
                        break
                    else:
                        proj.x = -100

        for pipe in self.pipes:
            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.coins += 1
                self.profile_totals["coins_collected"] = int(self.profile_totals.get("coins_collected", 0)) + 1
                self.profile_totals["pipes_scored"] = int(self.profile_totals.get("pipes_scored", 0)) + 1
                self.profile_totals["score_total"] = int(self.profile_totals.get("score_total", 0)) + 1
                self.run_stats["coins_earned"] += 1
                self.run_stats["pipes_scored"] += 1
                self.combo += 1
                self.run_stats["best_combo"] = max(int(self.run_stats.get("best_combo", 0)), int(self.combo))
                self.set_best_score(self.score)
                self.sounds.play("score")
                self.add_text("+1", self.bird.x + 10, self.bird.y - 24, (255, 255, 255))
                self.save_settings()
                self.evaluate_meta(award_rewards=True)
                self.add_burst(pipe.x + pipe.width, pipe.gap_y, self.bird.skin().accent, amount=8, speed=150)
                if self.boss_mode and self.boss:
                    pass

            top_rect, bot_rect = pipe.colliders()
            if self.bird.invuln <= 0 and (bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect)):
                self.hit_bird()
                break

        self.ambient_timer += dt
        if self.message_timer > 0:
            self.message_timer -= dt
        self.screen_shake = max(0.0, self.screen_shake - dt)
        self.flash = max(0.0, self.flash - dt)
        self.boss_hit_flash = max(0.0, self.boss_hit_flash - dt)
        if self.evaluate_meta(award_rewards=True):
            self.save_settings()

    def draw_background(self, surf: pygame.Surface, boss_preview_index: Optional[int] = None):
        t = self.time_alive * 0.9 + self.menu_scroll
        if self.boss_mode or boss_preview_index is not None:
            boss_idx = self.boss_index if boss_preview_index is None else boss_preview_index
            theme = BOSS_THEMES[boss_idx % len(BOSS_THEMES)]
            bg_kind = theme.get("bg_kind", "aegis")
            surf.blit(self.bg_cache[f"BOSS_{boss_idx % len(BOSS_THEMES)}"], (0, 0))
            draw_boss_background(surf, theme, bg_kind, t)
            if self.boss_mode and self.boss:
                draw_boss_cinematic_fx(surf, theme, bg_kind, self.boss, t)
            return

        theme = self.current_theme()
        scene = self.arcade_bg_cache[theme["name"]]
        surf.blit(scene["base"], (0, 0))
        surf.blit(scene["static"], (0, 0))

        kind = scene["kind"]
        haze = scene["haze"]
        cloud = scene["cloud"]
        pipe = scene["pipe"]
        pipe_dark = scene["pipe_dark"]

        # Gentle motion layer: only a few animated elements per frame.
        for i, (cloud_surf, seed_x, y, speed, phase) in enumerate(scene["clouds"]):
            x = ((seed_x - t * speed) % (WIDTH + 240)) - 120
            yy = y + math.sin(t * 0.34 + phase + i * 0.18) * (2.0 + i * 0.4)
            surf.blit(cloud_surf, (int(x), int(yy)))

        if kind == "DAWN":
            # Warm shimmer on the horizon.
            shimmer = 0.5 + 0.5 * math.sin(t * 0.55)
            pygame.draw.line(surf, haze, (0, 286), (WIDTH, 278), 2)
            pygame.draw.line(surf, theme["cloud"], (0, 272), (WIDTH, 268), 1)
            for i in range(7):
                x = 70 + i * 132 + int(math.sin(t * 0.8 + i) * 9)
                y = 116 + int(math.sin(t * 1.2 + i) * 4)
                pygame.draw.circle(surf, haze, (x, y), 2 if i % 3 == 0 else 1)

            # Animated sun: smooth breathing glow with subtle internal motion.
            sun = scene.get("sun", {})
            cx, cy = sun.get("center", (WIDTH - 150, 94))
            radius = sun.get("radius", 54)
            pulse = 0.5 - 0.5 * math.cos(t * 0.72)
            micro = 0.5 - 0.5 * math.cos(t * 0.18)
            sun_fx = get_clear_surface((240, 240), ("dawn_sun_fx",))
            center = (120, 120)
            glow_r = int(82 + pulse * 8)
            ring_r = int(98 + pulse * 5)
            core_r = int(radius * 0.95 + pulse * 2)
            pygame.draw.circle(sun_fx, (*haze, 24), center, glow_r)
            pygame.draw.circle(sun_fx, (*theme["cloud"], 78), center, ring_r, 8)
            pygame.draw.circle(sun_fx, (*theme["cloud"], 210), center, core_r)
            pygame.draw.circle(sun_fx, (*haze, 150), center, int(34 + pulse * 2))
            for k in range(12):
                ang = t * 0.16 + k * (math.tau / 12.0)
                sway = 0.92 + 0.08 * math.sin(t * 0.54 + k)
                r1 = 58 + pulse * 3
                r2 = 76 + pulse * 8
                x1 = center[0] + int(math.cos(ang) * r1)
                y1 = center[1] + int(math.sin(ang) * r1 * sway)
                x2 = center[0] + int(math.cos(ang) * r2)
                y2 = center[1] + int(math.sin(ang) * r2 * sway)
                pygame.draw.line(sun_fx, (*haze, 62), (x1, y1), (x2, y2), 2 if k % 2 == 0 else 1)
            spec_x = center[0] + int(math.cos(t * 0.34) * (9 + micro * 3))
            spec_y = center[1] + int(math.sin(t * 0.29) * (5 + micro * 2))
            pygame.draw.circle(sun_fx, (*WHITE, 110), (spec_x, spec_y), 4)
            surf.blit(sun_fx, sun_fx.get_rect(center=(cx, cy)))

            # More dynamic sky noise: drifting sparkles + shimmering atmosphere.
            for i, (sx, sy, size, phase, col) in enumerate(scene["sparkles"]):
                if (i + int(t * 2.0)) % 3 == 0:
                    continue
                alpha_size = size + (1 if shimmer > 0.7 and i % 2 == 0 else 0)
                xx = int((sx + t * 6) % WIDTH)
                yy = int(sy + math.sin(t * 0.9 + phase * 6.0) * 2)
                pygame.draw.circle(surf, col, (xx, yy), alpha_size)
            for i in range(3):
                x = 120 + i * 250 + int(math.sin(t * 0.35 + i) * 24)
                y = 190 + int(math.sin(t * 0.62 + i * 1.4) * 6)
                pygame.draw.arc(surf, (*haze, 60), (x - 96, y - 24, 192, 70), 0.12, 2.84, 2)

        elif kind == "NIGHT":
            # Mild parallax twinkles and drifting nocturnal mist.
            mist_y = 132 + int(math.sin(t * 0.24) * 6)
            pygame.draw.line(surf, (*haze, 64), (0, mist_y), (WIDTH, mist_y - 8), 1)
            for i, (sx, sy, size, phase, col) in enumerate(scene["sparkles"]):
                flicker = 0.5 + 0.5 * math.sin(t * (1.1 + (i % 3) * 0.07) + phase * math.tau)
                if flicker < 0.42:
                    continue
                star_x = sx + int(math.sin(t * 0.15 + phase * 8.0) * 2)
                star_y = sy + int(math.cos(t * 0.18 + phase * 5.0) * 1)
                pygame.draw.circle(surf, col, (star_x, star_y), 1 if size == 1 else 2)
            for i in range(4):
                x = 104 + i * 286 + int(math.sin(t * 0.35 + i) * 18)
                y = 148 + (i % 2) * 14 + int(math.sin(t * 0.9 + i) * 4)
                pygame.draw.arc(surf, haze, (x - 84, y - 18, 172, 56), 0.18, 2.95, 2)
            # Thin moon-halo sweep and drifting cloud wisps.
            sweep_x = int((math.sin(t * 0.17) * 0.5 + 0.5) * (WIDTH + 240)) - 120
            pygame.draw.arc(surf, (*cloud, 70), (sweep_x - 132, 36, 264, 96), 0.15, 2.95, 2)
            for i in range(6):
                x = (i * 182 + int(t * 20)) % (WIDTH + 180) - 90
                pygame.draw.line(surf, (*pipe_dark, 120), (x, 398 + (i % 2) * 4), (x + 54, 386 + (i % 2) * 4), 1)
            pygame.draw.line(surf, pipe_dark, (0, 406), (WIDTH, 390), 1)
            pygame.draw.line(surf, pipe, (0, 410), (WIDTH, 398), 1)

        elif kind == "EMBER":
            # Floating ash and heat ripples.
            for i, (sx, sy, size, phase, col) in enumerate(scene["sparkles"]):
                yy = sy - int((t * (18 + (i % 4) * 3)) % (HEIGHT + 40))
                xx = int((sx + math.sin(t * 0.8 + phase * 8.0) * 18) % WIDTH)
                if yy < -20:
                    yy += HEIGHT + 40
                pulse = 0.6 + 0.4 * math.sin(t * 1.4 + phase * 7.0)
                pygame.draw.circle(surf, col, (xx, yy), max(1, int(size * pulse)))
            for i in range(4):
                x = 92 + i * 206 + int(math.sin(t * 1.8 + i) * 11)
                pygame.draw.arc(surf, haze, (x - 64, 34, 132, 68), 0.22, 2.76, 2)
            for i in range(10):
                x = (i * 101 + int(t * 48)) % (WIDTH + 120) - 60
                wob = int(math.sin(t * 1.2 + i) * 6)
                pygame.draw.line(surf, pipe_dark, (x, HEIGHT - 122), (x + 26 + wob, HEIGHT - 76), 2)
            for i in range(5):
                x = 76 + i * 168 + int(math.sin(t * 0.52 + i) * 16)
                pygame.draw.circle(surf, (*haze, 88), (x, 122 + int(math.sin(t * 1.1 + i) * 8)), 3)

        else:  # AURORA
            # Slow sweeping light curtains with subtle gliding sparks.
            for i, band in enumerate(scene["ribbons"]):
                offset = math.sin(t * (0.45 + i * 0.08) + i * 1.3) * (10 + i * 2)
                shifted = [(x + int(offset), y + int(math.sin(t * 0.2 + x * 0.01) * 2)) for x, y in band]
                pygame.draw.lines(surf, haze if i != 1 else cloud, False, shifted, 2)
            sweep_x = int((math.sin(t * 0.28) * 0.5 + 0.5) * (WIDTH + 220)) - 110
            pygame.draw.arc(surf, haze, (sweep_x - 160, 38, 320, 118), 0.12, 2.96, 2)
            # Add layered glow ripples and slow spark drift so the scene never feels static.
            for i in range(3):
                x = 96 + i * 274 + int(math.sin(t * 0.23 + i) * 14)
                y = 82 + i * 18 + int(math.sin(t * 0.44 + i * 1.2) * 8)
                pygame.draw.arc(surf, (*haze, 62), (x - 150, y - 24, 300, 96), 0.15, 2.88, 2)
            for i, (sx, sy, size, phase, col) in enumerate(scene["sparkles"]):
                if (i + int(t * 3)) % 4 == 0:
                    continue
                yy = sy + int(math.sin(t * 0.8 + phase * 6.0) * 4)
                xx = sx + int(math.cos(t * 0.22 + phase * 4.0) * 2)
                pygame.draw.circle(surf, col, (xx, yy), size)

        # Finish with a slim ground strip to keep the horizon crisp.
        pygame.draw.rect(surf, pipe_dark, (0, HEIGHT - 14, WIDTH, 14))
        pygame.draw.rect(surf, pipe, (0, HEIGHT - 14, WIDTH, 4))



    def draw_ui(self, surf: pygame.Surface):
        theme = self.current_theme()
        draw_text(surf, self.font_big, self.current_mode.title(), (20, 14), WHITE)
        draw_text(surf, self.font, f"Score: {self.score}", (22, 68), theme["haze"])
        coins_earned = int(self.run_stats.get("coins_earned", 0))
        y = 96
        draw_text(surf, self.font, f"Best: {self.current_best_score()}", (22, y), theme["haze"])
        draw_text(surf, self.font, f"Coin: {coins_earned}", (22, y + 28), (255, 220, 120))
        draw_text(surf, self.font, f"Difficulty: {DIFFICULTIES[self.current_difficulty_index].name.title()}", (22, y + 56), (235, 235, 235))
        if self.boss_mode:
            draw_text(surf, self.font_small, f"Boss: {BOSS_SPECS[self.boss_index]['short']}", (22, y + 84), BOSS_SPECS[self.boss_index]["accent"])
        draw_text(surf, self.font_small, "Space / Up / Click = Flap", (WIDTH - 18, HEIGHT - 28), WHITE, align="right")
        if self.show_hitboxes:
            draw_text(surf, self.font_small, "HITBOX: ON", (WIDTH - 18, 56), (255, 220, 140), align="right", shadow=False)
        if self.state in ("PLAY", "PAUSE"):
            self.draw_pause_toggle_button(surf)

        effect_rows = []
        effect_labels = {
            "magnet": "MAGNET",
            "boost": "BOOST",
            "multiplier": "X2",
        }
        effect_colors = {
            "magnet": (255, 120, 120),
            "boost": (160, 255, 180),
            "multiplier": (255, 175, 255),
        }
        for key in ("magnet", "boost", "multiplier"):
            remaining = float(self.active_effects.get(key, 0.0))
            if remaining > 0:
                effect_rows.append((effect_labels[key], remaining, effect_colors[key]))
        if self.bird.shield > 0:
            effect_rows.append(("SHIELD", self.bird.shield, (120, 240, 255)))
        if self.bird.invuln > 0:
            effect_rows.append(("INVULN", self.bird.invuln, (255, 255, 255)))
        if self.bird.revives > 0:
            effect_rows.append((f"REVIVE X{self.bird.revives}", None, (255, 210, 120)))
        if effect_rows:
            start_x = 18
            start_y = HEIGHT - 58 - (len(effect_rows) - 1) * 16
            for i, (label, remaining, color) in enumerate(effect_rows[:7]):
                suffix = f" {remaining:0.1f}s" if remaining is not None else ""
                draw_text(surf, self.font_small, f"{label}{suffix}", (start_x, start_y + i * 16), color, align="left", shadow=False)
        if self.boss_mode and self.current_mode == "BOSS" and self.boss_intro > 0 and not getattr(self, "boss_intro_done", False):
            spec = BOSS_SPECS[self.boss_index]
            center_y = HEIGHT * 0.40
            panel_w = min(720, int(WIDTH * 0.70))
            panel_h = 124
            panel = pygame.Rect(WIDTH // 2 - panel_w // 2, int(center_y - panel_h / 2), panel_w, panel_h)
            overlay = get_clear_surface(panel.size, ("boss_intro_overlay", panel_w, panel_h))
            draw_round_rect(overlay, (10, 14, 22, 208), overlay.get_rect(), radius=26)
            draw_round_outline(overlay, spec["accent"], overlay.get_rect(), radius=26, width=2)
            t = self.boss_intro
            for i in range(5):
                xx = 24 + int((panel_w - 48) * ((i * 0.2 + t * 0.25) % 1.0))
                pygame.draw.line(overlay, (*spec["core"], 85), (xx, 18), (xx + 42, 18), 2)
            draw_text(overlay, self.font_huge, spec["name"], (panel_w // 2, 34), spec["accent"], center=True)
            desc_box = pygame.Rect(panel_w // 2 - 220, 70, 440, 32)
            draw_round_rect(overlay, (255, 255, 255, 10), desc_box, radius=16)
            draw_round_outline(overlay, spec["accent"], desc_box, radius=16, width=2)
            draw_text(overlay, self.font, sentence_case(spec["description"]), desc_box.center, spec["haze"] if "haze" in spec else theme["haze"], center=True, shadow=False)
            if self.boss_intro > 0.2:
                alpha = int(255 * clamp((self.boss_intro - 0.2) / 1.0, 0.0, 1.0))
                overlay.set_alpha(alpha)
            surf.blit(overlay, panel.topleft)
        elif self.message_timer > 0 and self.message:
            draw_text(surf, self.font_big, self.message, (WIDTH // 2, 70), theme["haze"], center=True)

    def draw_hud_overlays(self, surf: pygame.Surface):
        if self.flash > 0:
            surf.blit(self.get_overlay((WIDTH, HEIGHT), (255, 255, 255, int(90 * self.flash / 0.2))), (0, 0))
        if self.screen_shake > 0:
            pass

    def draw_hitboxes_overlay(self, surf: pygame.Surface):
        if not self.show_hitboxes:
            return

        overlay = self.hitbox_overlay
        overlay.fill((0, 0, 0, 0))

        # Bird
        bird_rect = self.bird.rect()
        pygame.draw.rect(overlay, (90, 255, 220, 240), bird_rect.inflate(2, 2), width=2, border_radius=7)

        # Pipes
        for pipe in self.pipes:
            top_rect, bot_rect = pipe.colliders()
            if top_rect.width > 0 and top_rect.height > 0:
                pygame.draw.rect(overlay, (255, 190, 90, 220), top_rect, width=2, border_radius=4)
            if bot_rect.width > 0 and bot_rect.height > 0:
                pygame.draw.rect(overlay, (255, 190, 90, 220), bot_rect, width=2, border_radius=4)

        # Boss projectiles
        for proj in self.projectiles:
            rect = proj.rect()
            draw_round_outline(overlay, (255, 120, 120, 230), rect.inflate(2, 2), radius=5, width=2)

        # Items / orbs
        for orb in self.orbs:
            if not orb.active:
                continue
            rect = orb.rect()
            draw_round_outline(overlay, (120, 210, 255, 210), rect.inflate(2, 2), radius=12, width=2)

        # Boss body / hurtbox
        if self.boss_mode and self.boss and not self.boss.dying:
            spec = self.boss.spec()
            hitbox_img, rect = draw_boss_hitbox_surface(spec, self.boss)
            draw_mask_outline(overlay, pygame.mask.from_surface(hitbox_img), rect.topleft, (210, 130, 255, 200), width=2)

        if self.boss_mode and self.boss and self.boss.dying:
            spec = self.boss.spec()
            hitbox_img, rect = draw_boss_hitbox_surface(spec, self.boss)
            draw_mask_outline(overlay, pygame.mask.from_surface(hitbox_img), rect.topleft, (255, 120, 80, 170), width=2)

        surf.blit(overlay, (0, 0))

    def draw_pipes_orbs_projectiles(self, surf: pygame.Surface):
        theme = self.current_theme()
        pulse = 0.5 + 0.5 * math.sin(self.time_alive * 4.0)
        boss_active = self.boss_mode and self.boss is not None
        boss_spec = self.boss.spec() if boss_active else None
        boss_phase = self.boss.phase if boss_active else 1
        boss_timer = self.boss.phase_timer if boss_active else self.time_alive
        ring_alpha = int(100 + 90 * pulse)

        for pipe in self.pipes:
            pipe.draw(surf, theme, pulse=pulse, boss_spec=boss_spec, boss_phase=boss_phase, boss_timer=boss_timer)
            if boss_active and self.boss.hp > 0:
                gap = pipe.gap_rect()
                if gap.width > 0:
                    phase = self.boss.phase
                    spec = boss_spec
                    ring = get_pipe_gap_ring_surface(
                        (gap.width + 54, gap.height + 54),
                        phase,
                        spec["accent"],
                        spec["core"],
                        alpha=ring_alpha,
                    )
                    surf.blit(ring, ring.get_rect(center=gap.center))

        bird_skin = self.bird.skin()
        for orb in self.orbs:
            orb.draw(surf, bird_skin)
        for proj in self.projectiles:
            proj.draw(surf)

    def draw_particles(self, surf: pygame.Surface):
        if not self.particles and not self.texts:
            return
        for p in self.particles:
            p.draw(surf)
        for t in self.texts:
            t.draw(surf, self.font)


    def draw_play(self):
        surf = self.screen
        self.draw_background(surf)
        # ── Boss environment background layer ─────────────────────────────────
        if self.boss_mode:
            self.draw_boss_env_bg_layer(surf)
        # ─────────────────────────────────────────────────────────────────────
        self.draw_pipes_orbs_projectiles(surf)
        self.bird.draw(surf)

        boss_needs_env_redraw = bool(
            self.boss_mode
            and self.boss
            and (
                (self.env_lightning_timer > 0 and bool(self.env_lightning_bolts))
                or self.env_darkness > 0.10
            )
        )
        if self.boss_mode and self.boss and not boss_needs_env_redraw:
            self.boss.draw(surf, self.font, self.current_difficulty())

        self.draw_particles(surf)
        # ── Boss environment foreground layer ────────────────────────────────
        if self.boss_mode:
            self.draw_boss_env_fg_layer(surf)
        # ─────────────────────────────────────────────────────────────────────
        self.draw_hitboxes_overlay(surf)
        # Boss entry fade: darkens game world only; boss description panel (drawn in draw_ui) is unaffected.
        if self.boss_mode and self.boss_entry_fade > 0:
            alpha = int(255 * self.boss_entry_fade / max(0.001, self.boss_entry_fade_total))
            self._boss_entry_fade_surf.set_alpha(alpha)
            surf.blit(self._boss_entry_fade_surf, (0, 0))
        self.draw_ui(surf)

        if self.state == "CLEAR":
            surf.blit(self.get_overlay((WIDTH, HEIGHT), (10, 14, 24, 180)), (0, 0))
            coins_earned = int(self.run_stats.get("coins_earned", 0))
            # ── "Victory!" — large pulsing gold title with multi-layer glow ───
            vic_y = HEIGHT // 2 - 72
            # Outer dark-gold shadow halo
            for gx, gy in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
                draw_text(surf, self.font_victory, "Victory!", (WIDTH // 2 + gx, vic_y + gy), (120, 76, 0), center=True, shadow=False)
            # Mid-tone warm glow
            for gx, gy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                draw_text(surf, self.font_victory, "Victory!", (WIDTH // 2 + gx, vic_y + gy), (210, 148, 0), center=True, shadow=False)
            # Bright gold core
            draw_text(surf, self.font_victory, "Victory!", (WIDTH // 2, vic_y), (255, 232, 40), center=True)
            draw_text(surf, self.font_big, f"Score: {self.score}  Coins: {coins_earned}", (WIDTH // 2, HEIGHT // 2 + 14), (255, 220, 150), center=True)
            draw_text(surf, self.font, "Esc = Menu   R = Replay", (WIDTH // 2, HEIGHT // 2 + 60), WHITE, center=True, shadow=False)
            self.draw_clear_buttons(surf)
        elif self.state == "GAME_OVER":

            surf.blit(self.get_overlay((WIDTH, HEIGHT), (12, 14, 20, 190)), (0, 0))
            draw_text(surf, self.font_huge, "Game Over", (WIDTH // 2, HEIGHT // 2 - 72), (255, 255, 255), center=True)
            coins_earned = int(self.run_stats.get("coins_earned", 0))
            draw_text(surf, self.font_big, f"Score: {self.score}  Coins: {coins_earned}  Best: {self.current_best_score()}", (WIDTH // 2, HEIGHT // 2), (255, 225, 170), center=True)
            draw_text(surf, self.font, "Esc = Menu   R = Replay", (WIDTH // 2, HEIGHT // 2 + 56), WHITE, center=True, shadow=False)
            self.draw_game_over_buttons(surf)

        if self.state in ("CLEAR", "GAME_OVER"):
            self.draw_run_summary(surf)

        self.draw_notifications(surf)
        self.draw_hud_overlays(surf)
        if self.screen_shake > 0:
            offset = (random.randint(-5, 5), random.randint(-4, 4))
            self.screen.blit(surf, offset)
        else:
            self.screen.blit(surf, (0, 0))

    def draw_menu(self):
        surf = self.screen
        self.draw_background(surf)
        surf.blit(self.get_overlay((WIDTH, HEIGHT), (10, 12, 20, 40)), (0, 0))

        title_y = 76
        title_text = GAME_TITLE if self.menu_page == "MAIN" else "Select Mode"
        draw_text(surf, self.font_huge, title_text, (WIDTH // 2, title_y), (255, 255, 255), center=True)

        for i, item in enumerate(self.menu_items):
            rect = self.menu_item_rect(i)
            active = i == self.menu_index
            txt = item.replace("START ARCADE", "Arcade Mode").replace("BOSS MODE", "Boss Mode").replace("SKINS", "Skins").replace("Profile", "Profile").replace("OPTIONS", "Options").replace("QUIT", "Quit")
            if item == "START ARCADE":
                txt = f"Arcade Mode [{DIFFICULTIES[self.current_difficulty_index].name.title()}]"
            self.draw_button(surf, rect, txt, active=active, flash=self.is_button_flashed(rect), font=self.font)
    def draw_skin_screen(self):
        surf = self.screen
        self.draw_background(surf)
        surf.blit(self.get_overlay((WIDTH, HEIGHT), (6, 10, 18, 80)), (0, 0))

        draw_text(surf, self.font_huge, "Skins", (WIDTH // 2, 44), WHITE, center=True)
        draw_text(surf, self.font_micro, "A / D / Left / Right or click the arrows to browse", (WIDTH // 2, 92), (235, 240, 248), center=True, shadow=False)

        skin = SKINS[self.skin_cursor]
        unlocked = self.skin_cursor in self.unlocked
        price = skin.cost

        card = self.skin_card_rect()
        prev_rect = self.skin_nav_rect(-1)
        next_rect = self.skin_nav_rect(1)

        self.draw_skin_nav_button(surf, prev_rect, -1, skin.accent, flash=self.is_button_flashed(prev_rect))
        self.draw_skin_nav_button(surf, next_rect, 1, skin.accent, flash=self.is_button_flashed(next_rect))

        draw_round_rect(surf, (18, 24, 38), card, radius=26)
        hovered = self.is_button_hovered(card)
        equipped = self.skin_index == self.skin_cursor
        selected = self.selected_skin == self.skin_cursor
        outline = WHITE if (skin.name == "CLASSIC" or hovered or equipped or selected) else skin.accent
        draw_round_outline(surf, outline, card, radius=26, width=3 if (hovered or equipped or selected or skin.name == "CLASSIC") else 2)
        self.draw_button_shine(surf, card, 26)
        if hovered:
            draw_round_flash(surf, card, 26, 18)
        if self.is_button_flashed(card):
            draw_round_flash(surf, card, 26, 52)

        bird_preview = Bird(card.centerx, card.y + 104, skin_index=self.skin_cursor)
        bird_preview.vy = -220
        bird_preview.draw(surf)

        draw_text(surf, self.font_big, skin.name.title(), (card.centerx, card.y + 188), WHITE, center=True)
        label = "Unlocked" if unlocked else f"{price} Coins"
        draw_text(surf, self.font, label, (card.centerx, card.y + 228), skin.accent if unlocked else (255, 220, 120), center=True, shadow=False)

        status_y = card.y + 258
        if not unlocked:
            draw_text(surf, self.font, f"You Have {self.coins} Coins", (card.centerx, status_y), WHITE, center=True, shadow=False)
        else:
            draw_text(surf, self.font, "Enter / Click Card To Equip", (card.centerx, status_y), WHITE, center=True, shadow=False)

        draw_text(surf, self.font_small, "Aesthetic Only. No Gameplay Advantage.", (WIDTH // 2, HEIGHT - 34), WHITE, center=True, shadow=False)
        if self.message_timer > 0:
            draw_text(surf, self.font, self.message, (WIDTH // 2, HEIGHT - 64), (255, 240, 170), center=True, shadow=False)
        self._draw_screen_close_btn(surf, self.skin_close_rect())
        self.draw_notifications(surf)

    def draw_difficulty_screen(self):
        surf = self.screen
        self.draw_background(surf)
        surf.blit(self.get_overlay((WIDTH, HEIGHT), (6, 10, 18, 90)), (0, 0))

        title = "Select Difficulty"
        if self.difficulty_mode_target == "BOSS":
            title = "Choose Bosses Difficulty"
        draw_text(surf, self.font_huge, title, (WIDTH // 2, 48), WHITE, center=True)

        hint = "↑↓ / W-S: Rows   ←→ / A-D: Columns   Enter: Select"
        draw_text(surf, self.font_micro, hint, (WIDTH // 2, 92), (210, 220, 235), center=True, shadow=False)

        for i, diff in enumerate(DIFFICULTIES):
            rect = self.difficulty_rect(i)
            active = i == self.difficulty_cursor
            hovered = self.is_button_hovered(rect)
            fill = (32, 44, 68) if (active or hovered) else (20, 28, 44)
            edge = WHITE if (active or hovered) else (65, 85, 120)
            draw_round_rect(surf, fill, rect, radius=22)
            draw_round_outline(surf, edge, rect, radius=22, width=3 if (active or hovered) else 2)
            self.draw_button_shine(surf, rect, 22)
            self.draw_pulse_overlay(surf, rect, 22, hovered=hovered, active=active, flash=self.is_button_flashed(rect), phase_shift=0.15)

            name_font = self.font_big if rect.width >= 300 else self.font
            detail_font = self.font_small
            draw_text(surf, name_font, diff.name.title(), (rect.centerx, rect.y + 22), WHITE, center=True, shadow=False)
            draw_text(surf, detail_font, f"Gap: {diff.pipe_gap}", (rect.centerx, rect.y + 48), (225, 235, 245), center=True, shadow=False)
            draw_text(surf, detail_font, f"Speed: {int(diff.pipe_speed)}", (rect.centerx, rect.y + 68), (225, 235, 245), center=True, shadow=False)
            draw_text(surf, detail_font, f"Power: {int(round(diff.power_rate * 100))}%", (rect.centerx, rect.y + 88), (225, 235, 245), center=True, shadow=False)

        draw_text(surf, self.font, "Easy Is Relaxed, Insane Is Brutal But Still Fair.", (WIDTH // 2, HEIGHT - 34), WHITE, center=True, shadow=False)

        # Nav arrows
        for d in (-1, 1):
            r = self.difficulty_nav_rect(d)
            self.draw_nav_arrow(surf, r, d, flash=self.is_button_flashed(r))

        self._draw_screen_close_btn(surf, self.difficulty_close_rect())
        self.draw_notifications(surf)

    def draw_boss_select_screen(self):
        surf = self.screen
        self.draw_background(surf, boss_preview_index=self.boss_index)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 10, 18, 90))
        surf.blit(overlay, (0, 0))

        draw_text(surf, self.font_huge, "Select Boss", (WIDTH // 2, 34), WHITE, center=True)
        current_spec = BOSS_SPECS[self.boss_index]
        current_name = current_spec["name"]
        draw_text(surf, self.font_big, current_name, (WIDTH // 2, 86), current_spec["accent"], center=True, shadow=False)

        visible = VISIBLE_BOSS_INDICES
        current_visible_pos = visible.index(self.boss_index) if self.boss_index in visible else 0
        for i, boss_idx in enumerate(visible):
            spec = BOSS_SPECS[boss_idx]
            rect = self.boss_select_rect(i)
            active = i == current_visible_pos
            hovered = self.is_button_hovered(rect)
            edge = spec["accent"]
            self.draw_button(surf, rect, "", active=active, flash=self.is_button_flashed(rect), font=self.font_small, accent=edge)
            draw_round_outline(surf, WHITE if (active or hovered or self.is_button_flashed(rect)) else edge, rect, radius=18, width=3 if (active or hovered or self.is_button_flashed(rect)) else 2)
            self.draw_pulse_overlay(surf, rect, 18, hovered=hovered, active=active, flash=self.is_button_flashed(rect), phase_shift=0.1)

            draw_text(surf, self.font_small, spec["name"], (rect.centerx, rect.y + 18), spec["accent"], center=True, shadow=False)
            draw_text(surf, self.font_micro, f"HP: {int(round(DIFFICULTIES[self.difficulty_cursor].boss_hp * spec['hp_mult']))}", (rect.centerx, rect.y + 41), WHITE, center=True, shadow=False)
            draw_text(surf, self.font_micro, spec["attack"].title(), (rect.centerx, rect.y + 58), spec["accent"], center=True, shadow=False)

        draw_text(surf, self.font_small, f"Difficulty: {DIFFICULTIES[self.difficulty_cursor].name.title()}", (WIDTH // 2, HEIGHT - 16), (200, 200, 200), center=True, shadow=False)

        # Nav arrows
        for d in (-1, 1):
            r = self.boss_nav_rect(d)
            self.draw_nav_arrow(surf, r, d, flash=self.is_button_flashed(r))

        self._draw_screen_close_btn(surf, self.boss_select_close_rect())
        self.draw_notifications(surf)

    def draw_options_screen(self):
        surf = self.screen
        self.draw_background(surf)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 10, 18, 90))
        surf.blit(overlay, (0, 0))

        panel = self.option_panel_rect()
        draw_round_rect(surf, (14, 18, 32), panel, radius=28)
        draw_round_outline(surf, (96, 118, 154), panel, radius=28, width=2)
        self.draw_button_shine(surf, panel, 28)

        draw_text(surf, self.font_big, "Options", (panel.centerx, panel.y + 34), WHITE, center=True, shadow=False)

        close_rect = self.option_close_rect()
        self._draw_screen_close_btn(surf, close_rect)

        for i, item in enumerate(self.option_items()):
            rect = self.option_rect(i)
            active = i == self.options_index
            self.draw_option_card(surf, rect, item, active=active, flash=self.is_button_flashed(rect))

        reset_rect = self.option_reset_rect()
        self.draw_button(
            surf,
            reset_rect,
            "Restart",
            active=self.options_index == len(self.option_items()),
            flash=self.is_button_flashed(reset_rect),
            font=self.font,
            accent=(255, 152, 132),
        )

        draw_text(surf, self.font_micro, "Enter / click the selected control. Esc or X closes.", (WIDTH // 2, HEIGHT - 30), (235, 240, 248), center=True, shadow=False)
        if self.message_timer > 0:
            draw_text(surf, self.font_small, self.message, (WIDTH // 2, panel.bottom + 12), (255, 240, 170), center=True, shadow=False)

        self.draw_notifications(surf)

    def options_reset_confirm_rect(self) -> pygame.Rect:
        return pygame.Rect(WIDTH // 2 - 222, HEIGHT // 2 - 122, 444, 244)

    def options_reset_yes_rect(self) -> pygame.Rect:
        modal = self.options_reset_confirm_rect()
        return pygame.Rect(modal.x + 38, modal.bottom - 74, 146, 46)

    def options_reset_no_rect(self) -> pygame.Rect:
        modal = self.options_reset_confirm_rect()
        return pygame.Rect(modal.right - 184, modal.bottom - 74, 146, 46)

    def draw_options_reset_confirm(self, surf: pygame.Surface):
        modal = self.options_reset_confirm_rect()
        draw_round_rect(surf, (14, 18, 30), modal, radius=26)
        draw_round_outline(surf, (180, 192, 214), modal, radius=26, width=2)
        self.draw_button_shine(surf, modal, 26)
        gloss = pygame.Surface(modal.size, pygame.SRCALPHA)
        pygame.draw.rect(gloss, (255, 255, 255, 12), gloss.get_rect(), border_radius=26)
        surf.blit(gloss, modal.topleft)

        return

    def apply_options_restart(self):
        self.best_scores = {}
        self.coins = 0
        self.profile_totals = self.default_profile_totals()
        self.achievements = set()
        self.quest_state = {}
        self.ensure_quest_state(force=True)
        self.pending_quest_reward = 0
        self.profile_tab = "stats"
        self.profile_achievement_index = 0
        self.options_reset_confirm = False
        self.options_reset_confirm_choice = 0
        self.last_run_summary = {}
        self.message = ""
        self.message_timer = 0.0
        self.save_settings()

    def draw_pause(self):
        surf = self.screen
        self.draw_background(surf)
        self.draw_pipes_orbs_projectiles(surf)
        self.bird.draw(surf)
        if self.boss_mode and self.boss:
            self.boss.draw(surf, self.font, self.current_difficulty())
        self.draw_particles(surf)
        self.draw_ui(surf)
        surf.blit(self.get_overlay((WIDTH, HEIGHT), (8, 12, 20, 165)), (0, 0))
        panel = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 122, 500, 244)
        draw_round_rect(surf, (14, 18, 30), panel, radius=28)
        draw_round_rect(surf, (72, 92, 132), panel, radius=28, width=2)
        self.draw_button_shine(surf, panel, 28)
        draw_text(surf, self.font_huge, "Paused", (WIDTH // 2, HEIGHT // 2 - 78), WHITE, center=True)
        draw_text(surf, self.font, "P or Esc = Resume", (WIDTH // 2, HEIGHT // 2 - 22), WHITE, center=True, shadow=False)
        draw_text(surf, self.font, "R = Replay", (WIDTH // 2, HEIGHT // 2 + 10), WHITE, center=True, shadow=False)
        draw_text(surf, self.font_micro, "Use the buttons below too", (WIDTH // 2, HEIGHT // 2 + 34), (205, 215, 230), center=True, shadow=False)
        self.draw_pause_buttons(surf)
        self.draw_notifications(surf)
        self.screen.blit(surf, (0, 0))

    def draw_pause_buttons(self, surf: pygame.Surface):
        buttons = (
            ("RESUME", "Resume"),
            ("REPLAY", "Replay"),
            ("MENU", "Menu"),
        )
        for kind, label in buttons:
            rect = self.pause_button_rect(kind)
            self.draw_button(surf, rect, label, flash=self.is_button_flashed(rect), accent=(255, 220, 140))

    def click_pause_button(self, pos) -> bool:
        resume_rect = self.pause_button_rect("RESUME")
        replay_rect = self.pause_button_rect("REPLAY")
        menu_rect = self.pause_button_rect("MENU")
        if resume_rect.collidepoint(pos):
            self.trigger_button_flash(resume_rect)
            self.state = "PLAY"
            return True
        if replay_rect.collidepoint(pos):
            self.trigger_button_flash(replay_rect)
            self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
            return True
        if menu_rect.collidepoint(pos):
            self.trigger_button_flash(menu_rect)
            self.state = "MENU"
            self.save_settings()
            return True
        return False

    def handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.menu_page == "MAIN":
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                    self.sounds.play("click")
                    self.trigger_button_flash(self.menu_item_rect(self.menu_index))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                    self.sounds.play("click")
                    self.trigger_button_flash(self.menu_item_rect(self.menu_index))
                elif event.key == pygame.K_RETURN:
                    self.trigger_button_flash(self.menu_item_rect(self.menu_index))
                    self.activate_menu_item()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.menu_items[self.menu_index] == "SKINS":
                        self.skin_index = (self.skin_index - 1) % len(SKINS)
                        self.selected_skin = self.skin_index
                        self.sounds.play("click")
                        self.trigger_button_flash(self.menu_item_rect(self.menu_index))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.menu_items[self.menu_index] == "SKINS":
                        self.skin_index = (self.skin_index + 1) % len(SKINS)
                        self.selected_skin = self.skin_index
                        self.sounds.play("click")
                        self.trigger_button_flash(self.menu_item_rect(self.menu_index))
            else:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.play_index = (self.play_index - 1) % 3
                    self.sounds.play("click")
                    self.trigger_button_flash(self.play_card_rect(self.play_index))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.play_index = (self.play_index + 1) % 3
                    self.sounds.play("click")
                    self.trigger_button_flash(self.play_card_rect(self.play_index))
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.play_index = (self.play_index - 1) % 3
                    self.sounds.play("click")
                    self.trigger_button_flash(self.play_card_rect(self.play_index))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.play_index = (self.play_index + 1) % 3
                    self.sounds.play("click")
                    self.trigger_button_flash(self.play_card_rect(self.play_index))
                elif event.key == pygame.K_RETURN:
                    self.trigger_button_flash(self.play_card_rect(self.play_index))
                    self.activate_menu_item()
                elif event.key == pygame.K_ESCAPE:
                    self.menu_page = "MAIN"
                    self.sounds.play("click")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_page == "MAIN":
                for i in range(len(self.menu_items)):
                    rect = self.menu_item_rect(i)
                    if rect.collidepoint(event.pos):
                        self.menu_index = i
                        self.trigger_button_flash(rect)
                        self.activate_menu_item()
                        break
            else:
                prev_r = self.play_mode_nav_rect(-1)
                next_r = self.play_mode_nav_rect(1)
                if prev_r.collidepoint(event.pos):
                    self.play_index = (self.play_index - 1) % 3
                    self.sounds.play("click")
                    self.trigger_button_flash(prev_r)
                    return
                if next_r.collidepoint(event.pos):
                    self.play_index = (self.play_index + 1) % 3
                    self.sounds.play("click")
                    self.trigger_button_flash(next_r)
                    return
                for i in range(3):
                    rect = self.play_card_rect(i)
                    if rect.collidepoint(event.pos):
                        self.play_index = i
                        self.trigger_button_flash(rect)
                        self.activate_menu_item()
                        return
                back = self.play_back_rect()
                if back.collidepoint(event.pos):
                    self.trigger_button_flash(back)
                    self.menu_page = "MAIN"
                    self.sounds.play("click")

    def activate_menu_item(self):
        if self.menu_page == "PLAY":
            self.sounds.play("click")
            if self.play_index == 0:
                self.difficulty_mode_target = "ARCADE"
                self.state = "DIFFICULTY"
            elif self.play_index == 1:
                self.difficulty_mode_target = "BOSS"
                self.state = "DIFFICULTY"
            else:
                hell_index = len(BOSS_SPECS) - 1
                self.start_game("BOSS", len(DIFFICULTIES) - 1, hell_index)
            return

        item = self.menu_items[self.menu_index]
        self.sounds.play("click")
        self.trigger_button_flash(self.menu_item_rect(self.menu_index))
        if item == "PLAY":
            self.menu_page = "PLAY"
            self.play_index = 0
        elif item == "SKINS":
            self.skin_cursor = self.skin_index
            self.state = "SKINS"
        elif item == "Profile":
            self.state = "PROFILE"
        elif item == "OPTIONS":
            self.options_index = 0
            self.state = "OPTIONS"
        elif item == "QUIT":
            self.running = False

    def draw_menu(self):
        surf = self.screen
        self.draw_background(surf)
        surf.blit(self.get_overlay((WIDTH, HEIGHT), (10, 12, 20, 40)), (0, 0))

        title_y = 76
        title_text = GAME_TITLE if self.menu_page == "MAIN" else "Select Mode"
        draw_text(surf, self.font_huge, title_text, (WIDTH // 2, title_y), (255, 255, 255), center=True)
        if self.menu_page == "MAIN":
            draw_text(surf, self.font, "A Fresh Flappy Style Arcade", (WIDTH // 2, title_y + 52), (230, 240, 255), center=True, shadow=False)
            for i, item in enumerate(self.menu_items):
                rect = self.menu_item_rect(i)
                active = i == self.menu_index
                label_font = self.font if active else self.font
                txt = item
                if item == "PLAY":
                    txt = "Play"
                elif item == "Profile":
                    txt = "Profile"
                elif item == "OPTIONS":
                    txt = "Options"
                elif item == "SKINS":
                    txt = "Skins"
                elif item == "QUIT":
                    txt = "Quit"
                self.draw_button(surf, rect, txt, active=active, flash=self.is_button_flashed(rect), font=label_font)
        else:
            if self.menu_page == "PLAY":
                draw_text(surf, self.font, "Pick the flight lane you want to enter.", (WIDTH // 2, title_y + 48), (230, 240, 255), center=True, shadow=False)
                modes = ["ARCADE", "BOSS", "HELL"]
                for i, kind in enumerate(modes):
                    rect = self.play_card_rect(i)
                    active = i == self.play_index
                    self.draw_play_card(surf, rect, kind, active=active, flash=self.is_button_flashed(rect))
                # Nav arrows for mode selection
                for d in (-1, 1):
                    r = self.play_mode_nav_rect(d)
                    self.draw_nav_arrow(surf, r, d, flash=self.is_button_flashed(r))
            back = self.play_back_rect()
            self.draw_button(surf, back, "Back", active=False, flash=self.is_button_flashed(back), font=self.font, accent=(255, 255, 255))
        self.draw_notifications(surf)

    def handle_skin_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.cycle_skin(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.cycle_skin(1)
            elif event.key == pygame.K_ESCAPE:
                self.state = "MENU"
            elif event.key == pygame.K_RETURN:
                self.activate_skin_card()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = self.skin_close_rect()
            if close_rect.collidepoint(event.pos):
                self.trigger_button_flash(close_rect)
                self.sounds.play("click")
                self.state = "MENU"
                self.save_settings()
                return
            card = self.skin_card_rect()
            prev_rect = self.skin_nav_rect(-1)
            next_rect = self.skin_nav_rect(1)
            if prev_rect.collidepoint(event.pos):
                self.cycle_skin(-1)
                return
            if next_rect.collidepoint(event.pos):
                self.cycle_skin(1)
                return
            if card.collidepoint(event.pos):
                self.activate_skin_card()

    def handle_difficulty_event(self, event):
        if event.type == pygame.KEYDOWN:
            cols = 2
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.difficulty_cursor = (self.difficulty_cursor - 1) % len(DIFFICULTIES)
                self.sounds.play("click")
                self.trigger_button_flash(self.difficulty_rect(self.difficulty_cursor))
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.difficulty_cursor = (self.difficulty_cursor + 1) % len(DIFFICULTIES)
                self.sounds.play("click")
                self.trigger_button_flash(self.difficulty_rect(self.difficulty_cursor))
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.difficulty_cursor = (self.difficulty_cursor - cols) % len(DIFFICULTIES)
                self.sounds.play("click")
                self.trigger_button_flash(self.difficulty_rect(self.difficulty_cursor))
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.difficulty_cursor = (self.difficulty_cursor + cols) % len(DIFFICULTIES)
                self.sounds.play("click")
                self.trigger_button_flash(self.difficulty_rect(self.difficulty_cursor))
            elif event.key == pygame.K_RETURN:
                self.trigger_button_flash(self.difficulty_rect(self.difficulty_cursor))
                if self.difficulty_mode_target == "BOSS":
                    if self.boss_index not in VISIBLE_BOSS_INDICES:
                        self.boss_index = VISIBLE_BOSS_INDICES[0]
                    self.state = "BOSS_SELECT"
                else:
                    self.start_game(self.difficulty_mode_target, self.difficulty_cursor, self.boss_index)
            elif event.key == pygame.K_ESCAPE:
                self.state = "MENU"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = self.difficulty_close_rect()
            if close_rect.collidepoint(event.pos):
                self.trigger_button_flash(close_rect)
                self.sounds.play("click")
                self.state = "MENU"
                self.save_settings()
                return
            prev_r = self.difficulty_nav_rect(-1)
            next_r = self.difficulty_nav_rect(1)
            if prev_r.collidepoint(event.pos):
                self.difficulty_cursor = (self.difficulty_cursor - 1) % len(DIFFICULTIES)
                self.sounds.play("click")
                self.trigger_button_flash(prev_r)
                return
            if next_r.collidepoint(event.pos):
                self.difficulty_cursor = (self.difficulty_cursor + 1) % len(DIFFICULTIES)
                self.sounds.play("click")
                self.trigger_button_flash(next_r)
                return
            for i in range(len(DIFFICULTIES)):
                rect = self.difficulty_rect(i)
                if rect.collidepoint(event.pos):
                    self.difficulty_cursor = i
                    self.trigger_button_flash(rect)
                    self.sounds.play("click")
                    if self.difficulty_mode_target == "BOSS":
                        if self.boss_index not in VISIBLE_BOSS_INDICES:
                            self.boss_index = VISIBLE_BOSS_INDICES[0]
                        self.state = "BOSS_SELECT"
                    else:
                        self.start_game(self.difficulty_mode_target, self.difficulty_cursor, self.boss_index)
                    break

    def handle_boss_select_event(self, event):
        if event.type == pygame.KEYDOWN:
            visible = VISIBLE_BOSS_INDICES
            current_pos = visible.index(self.boss_index) if self.boss_index in visible else 0
            if event.key in (pygame.K_LEFT, pygame.K_a):
                current_pos = (current_pos - 1) % len(visible)
                self.boss_index = visible[current_pos]
                self.sounds.play("click")
                self.trigger_button_flash(self.boss_select_rect(current_pos))
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                current_pos = (current_pos + 1) % len(visible)
                self.boss_index = visible[current_pos]
                self.sounds.play("click")
                self.trigger_button_flash(self.boss_select_rect(current_pos))
            elif event.key == pygame.K_UP:
                current_pos = (current_pos - 4) % len(visible)
                self.boss_index = visible[current_pos]
                self.sounds.play("click")
                self.trigger_button_flash(self.boss_select_rect(current_pos))
            elif event.key == pygame.K_DOWN:
                current_pos = (current_pos + 4) % len(visible)
                self.boss_index = visible[current_pos]
                self.sounds.play("click")
                self.trigger_button_flash(self.boss_select_rect(current_pos))
            elif event.key == pygame.K_RETURN:
                self.trigger_button_flash(self.boss_select_rect(current_pos))
                self.start_game("BOSS", self.difficulty_cursor, self.boss_index)
            elif event.key == pygame.K_ESCAPE:
                self.state = "DIFFICULTY"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = self.boss_select_close_rect()
            if close_rect.collidepoint(event.pos):
                self.trigger_button_flash(close_rect)
                self.sounds.play("click")
                self.state = "DIFFICULTY"
                return
            visible = VISIBLE_BOSS_INDICES
            current_pos = visible.index(self.boss_index) if self.boss_index in visible else 0
            prev_r = self.boss_nav_rect(-1)
            next_r = self.boss_nav_rect(1)
            if prev_r.collidepoint(event.pos):
                current_pos = (current_pos - 1) % len(visible)
                self.boss_index = visible[current_pos]
                self.sounds.play("click")
                self.trigger_button_flash(prev_r)
                return
            if next_r.collidepoint(event.pos):
                current_pos = (current_pos + 1) % len(visible)
                self.boss_index = visible[current_pos]
                self.sounds.play("click")
                self.trigger_button_flash(next_r)
                return
            for i, boss_idx in enumerate(VISIBLE_BOSS_INDICES):
                rect = self.boss_select_rect(i)
                if rect.collidepoint(event.pos):
                    self.boss_index = boss_idx
                    self.trigger_button_flash(rect)
                    self.sounds.play("click")
                    self.start_game("BOSS", self.difficulty_cursor, self.boss_index)
                    return

    def activate_option(self, index: int):
        if index == 0:
            self.set_sound_enabled(not self.sound_on)
            self.message = "Sound On" if self.sound_on else "Sound Off"
            self.message_timer = 0.9
            return

        if index == 1:
            self.sounds.play("click")
            self.message = "Use Restart to clear all progress"
        elif index == 2:
            self.sounds.play("click")
            self.message = "Use Restart to clear all progress"
        elif index == 3:
            self.sounds.play("click")
            self.apply_options_restart()
        else:
            return
        self.message_timer = 1.0
        self.save_settings()

    def handle_options_event(self, event):
        option_count = len(self.option_items()) + 1

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.options_index = (self.options_index - 1) % option_count
                self.sounds.play("click")
                self.trigger_button_flash(self.option_target_rect(self.options_index))
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.options_index = (self.options_index + 1) % option_count
                self.sounds.play("click")
                self.trigger_button_flash(self.option_target_rect(self.options_index))
            elif event.key == pygame.K_RETURN:
                self.trigger_button_flash(self.option_target_rect(self.options_index))
                self.activate_option(self.options_index)
            elif event.key == pygame.K_ESCAPE:
                self.state = "MENU"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            close_rect = self.option_close_rect()
            prev_r = self.options_nav_rect(-1)
            next_r = self.options_nav_rect(1)
            option_count = len(self.option_items()) + 1
            if close_rect.collidepoint(event.pos):
                self.trigger_button_flash(close_rect)
                self.sounds.play("click")
                self.state = "MENU"
                self.save_settings()
                return
            if prev_r.collidepoint(event.pos):
                self.options_index = (self.options_index - 1) % option_count
                self.sounds.play("click")
                self.trigger_button_flash(prev_r)
                return
            if next_r.collidepoint(event.pos):
                self.options_index = (self.options_index + 1) % option_count
                self.sounds.play("click")
                self.trigger_button_flash(next_r)
                return
            for i in range(len(self.option_items())):
                rect = self.option_rect(i)
                if rect.collidepoint(event.pos):
                    self.options_index = i
                    self.trigger_button_flash(rect)
                    self.activate_option(i)
                    return
            reset_rect = self.option_reset_rect()
            if reset_rect.collidepoint(event.pos):
                self.options_index = len(self.option_items())
                self.trigger_button_flash(reset_rect)
                self.activate_option(self.options_index)
                return

    def handle_play_event(self, event):
        if self.boss_clear_pending:
            return
        if event.type == pygame.KEYDOWN:
            if self.state == "PLAY":
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.bird.flap(self.current_difficulty().flap)
                    self.run_stats["flaps"] += 1
                    self.profile_totals["flaps"] = int(self.profile_totals.get("flaps", 0)) + 1
                    self.sounds.play("flap")
                    self.spawn_skin_trail_fx(self.bird.x - 16, self.bird.y + 8, self.bird.skin(), strong=False)
                    self.evaluate_meta(award_rewards=True)
                elif event.key == pygame.K_p:
                    self.state = "PAUSE"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "PAUSE"

            elif self.state == "PAUSE":
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = "PLAY"
                elif event.key == pygame.K_r:
                    self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
                elif event.key == pygame.K_RETURN:
                    self.state = "PLAY"

            elif self.state == "GAME_OVER":
                if event.key == pygame.K_r:
                    self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.save_settings()

            elif self.state == "CLEAR":
                if event.key == pygame.K_r:
                    self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.save_settings()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state in ("PLAY", "PAUSE") and self.click_pause_toggle_button(event.pos):
                self.sounds.play("click")
                return
            if self.state == "PLAY":
                self.bird.flap(self.current_difficulty().flap)
                self.run_stats["flaps"] += 1
                self.profile_totals["flaps"] = int(self.profile_totals.get("flaps", 0)) + 1
                self.sounds.play("flap")
                self.spawn_skin_trail_fx(self.bird.x - 16, self.bird.y + 8, self.bird.skin(), strong=False)
                self.evaluate_meta(award_rewards=True)
            elif self.state == "PAUSE":
                if self.click_pause_button(event.pos):
                    return
            elif self.state == "GAME_OVER":
                if self.click_game_over_button(event.pos):
                    return
            elif self.state == "CLEAR":
                if self.click_clear_button(event.pos):
                    return

    def draw_game_over_buttons(self, surf: pygame.Surface):
        replay_rect = self.game_over_button_rect("REPLAY")
        menu_rect = self.game_over_button_rect("MENU")
        for rect, label in ((replay_rect, "Replay"), (menu_rect, "Menu")):
            self.draw_button(surf, rect, label.title(), flash=self.is_button_flashed(rect), accent=(255, 220, 140))

    def draw_clear_buttons(self, surf: pygame.Surface):
        menu_rect = self.clear_button_rect("MENU")
        replay_rect = self.clear_button_rect("REPLAY")
        for rect, label in ((menu_rect, "Menu"), (replay_rect, "Replay")):
            self.draw_button(surf, rect, label.title(), flash=self.is_button_flashed(rect), accent=(255, 220, 140))

    def click_game_over_button(self, pos) -> bool:
        replay_rect = self.game_over_button_rect("REPLAY")
        menu_rect = self.game_over_button_rect("MENU")
        if replay_rect.collidepoint(pos):
            self.trigger_button_flash(replay_rect)
            self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
            return True
        if menu_rect.collidepoint(pos):
            self.trigger_button_flash(menu_rect)
            self.state = "MENU"
            self.save_settings()
            return True
        return False

    def click_clear_button(self, pos) -> bool:
        menu_rect = self.clear_button_rect("MENU")
        replay_rect = self.clear_button_rect("REPLAY")
        if replay_rect.collidepoint(pos):
            self.trigger_button_flash(replay_rect)
            self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
            return True
        if menu_rect.collidepoint(pos):
            self.trigger_button_flash(menu_rect)
            self.state = "MENU"
            self.save_settings()
            return True
        return False

    # ── EASTER EGG ──────────────────────────────────────────────────────────
    def _start_matrix_egg(self):
        self.state = "MATRIX_EGG"
        self.egg_phase = "matrix_intro"
        self.egg_timer = 0.0
        self.egg_total_timer = 0.0
        self.egg_msg_index = 0
        self.egg_chaos_frames = 0
        self.egg_glitch_sound_timer = 0.0
        self.egg_type_chars = 0
        self.egg_type_timer = 0.0
        self.egg_fx_strength = 0.0
        self.egg_bsod_entered = False        # one-shot BSOD shock sound flag
        self.egg_hex_offset = 0.0            # scrolling hex dump offset
        self.egg_chaos_surge_played = False  # one-shot chaos surge flag
        self.egg_pixel_sparks: list = []     # pixel explosion sparks in chaos
        self.egg_bsod_glitch_t = 0.0         # BSOD exit glitch progress
        self.sounds.stop_channel(self.egg_noise_channel)
        self.egg_noise_channel = self.sounds.play_loop("egg_ambient", 0.04)

        # Half-width katakana + matrix symbols for authentic look
        KATAKANA = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
        MATRIX_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*<>{}[]|/\\" + KATAKANA + "█▓▒░"
        # Denser columns: 160 + random sub-columns
        n_cols = 164
        self.egg_matrix_cols = []
        self.egg_char_h = 12   # tighter vertical spacing → denser rain
        for i in range(n_cols):
            col_x  = int(i * WIDTH / n_cols) + random.randint(-3, 3)
            length = random.randint(14, 42)
            speed  = random.uniform(90, 310)
            head_y = random.uniform(-HEIGHT * 1.2, 0)
            chars  = [random.choice(MATRIX_CHARS) for _ in range(length)]
            tint   = random.choices([0, 1, 2], weights=[70, 20, 10])[0]  # 0=green,1=cyan,2=pale
            self.egg_matrix_cols.append({
                "x": col_x, "head_y": head_y,
                "chars": chars, "speed": speed, "length": length,
                "tint": tint, "chars_src": MATRIX_CHARS,
            })

    def _update_matrix_cols(self, dt: float):
        phase_boost = 1.0
        if self.egg_phase == "messages":
            phase_boost = 1.15
        elif self.egg_phase == "pause":
            phase_boost = 1.28
        elif self.egg_phase == "glitch_text":
            phase_boost = 1.55
        elif self.egg_phase in ("chaos", "bsod"):
            phase_boost = 2.10
        char_h = getattr(self, "egg_char_h", 12)
        for col in self.egg_matrix_cols:
            col["head_y"] += col["speed"] * dt * phase_boost
            if col["head_y"] > HEIGHT + col["length"] * char_h + 20:
                col["head_y"] = random.uniform(-220, -16)
                col["speed"]  = random.uniform(88, 330)
                if random.random() < 0.40:
                    src = col.get("chars_src", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                    col["chars"] = [random.choice(src) for _ in range(col["length"])]
            # Mutation rate climbs with intensity
            if self.egg_phase in ("matrix_intro", "messages"):
                mutate_rate = 0.14
            elif self.egg_phase == "pause":
                mutate_rate = 0.22
            elif self.egg_phase == "glitch_text":
                mutate_rate = 0.38
            else:
                mutate_rate = 0.60
            if random.random() < mutate_rate:
                src = col.get("chars_src", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                idx = random.randint(0, len(col["chars"]) - 1)
                col["chars"][idx] = random.choice(src)
            # Heavy corruption in glitch/chaos/bsod
            if self.egg_phase in ("glitch_text", "chaos", "bsod") and random.random() < 0.16:
                idx = random.randint(0, len(col["chars"]) - 1)
                col["chars"][idx] = random.choice("█▓▒░@#%&?/ｱｲｳｴｵ")

    def update_matrix_egg(self, dt: float):
        self.egg_timer += dt
        self.egg_total_timer += dt
        self._update_matrix_cols(dt)

        if self.egg_phase == "matrix_intro":
            self.egg_fx_strength = lerp(self.egg_fx_strength, 0.15, 0.035)
            if self.egg_timer >= 2.8:
                self.egg_phase = "messages"
                self.egg_timer = 0.0

        elif self.egg_phase == "messages":
            self.egg_fx_strength = lerp(self.egg_fx_strength, 0.30, 0.045)
            if self.egg_msg_index < len(EGG_MESSAGES):
                msg_len = len(EGG_MESSAGES[self.egg_msg_index])
                if self.egg_type_chars < msg_len:
                    self.egg_type_timer += dt
                    chars_now = int(self.egg_type_timer / 0.052)
                    if chars_now > 0:
                        self.egg_type_timer -= chars_now * 0.052
                        for _ in range(chars_now):
                            if self.egg_type_chars < msg_len:
                                self.egg_type_chars += 1
                                self.sounds.play("typewriter")
            if self.egg_timer >= 5.0:
                self.egg_msg_index += 1
                self.egg_timer = 0.0
                self.egg_type_chars = 0
                self.egg_type_timer = 0.0
                if self.egg_msg_index >= len(EGG_MESSAGES):
                    self.egg_phase = "pause"
                    self.egg_timer = 0.0

        elif self.egg_phase == "pause":
            self.egg_fx_strength = lerp(self.egg_fx_strength, 0.52, 0.05)
            if self.egg_timer >= 3.2:
                self.egg_phase = "glitch_text"
                self.egg_timer = 0.0

        elif self.egg_phase == "glitch_text":
            self.egg_fx_strength = lerp(self.egg_fx_strength, 0.80, 0.065)
            self.egg_glitch_sound_timer -= dt
            if self.egg_glitch_sound_timer <= 0:
                self.sounds.play("glitch")
                self.egg_glitch_sound_timer = random.uniform(0.08, 0.22)
            if self.egg_timer >= 5.0:
                self.egg_phase = "chaos"
                self.egg_timer = 0.0
                self.egg_chaos_surge_played = False

        elif self.egg_phase == "chaos":
            # Noise surges to max in chaos
            self.egg_fx_strength = lerp(self.egg_fx_strength, 1.0, 0.14)
            self.egg_hex_offset += dt * 300
            self.egg_chaos_frames += 1
            self.egg_glitch_sound_timer -= dt
            if self.egg_glitch_sound_timer <= 0:
                self.sounds.play(random.choice(["glitch", "glitch_hard", "static_crackle"]))
                self.egg_glitch_sound_timer = random.uniform(0.025, 0.07)
            # Play the chaos surge once (rising swell)
            if not self.egg_chaos_surge_played and self.egg_timer >= 0.1:
                self.sounds.play("chaos_surge")
                self.egg_chaos_surge_played = True
            # Spawn pixel sparks
            if random.random() < 0.55:
                for _ in range(random.randint(3, 10)):
                    self.egg_pixel_sparks.append({
                        "x": random.uniform(0, WIDTH),
                        "y": random.uniform(0, HEIGHT),
                        "vx": random.uniform(-220, 220),
                        "vy": random.uniform(-180, 180),
                        "life": random.uniform(0.15, 0.55),
                        "max_life": 0.55,
                        "c": random.choice([(0,255,80),(255,80,0),(255,0,80),(80,80,255),(255,255,0),(0,255,255)]),
                        "sz": random.randint(2, 7),
                    })
            # Update sparks
            for sp in self.egg_pixel_sparks:
                sp["x"] += sp["vx"] * dt
                sp["y"] += sp["vy"] * dt
                sp["life"] -= dt
            self.egg_pixel_sparks = [s for s in self.egg_pixel_sparks if s["life"] > 0]
            if self.egg_timer >= 3.8:
                self.egg_phase = "bsod"
                self.egg_timer = 0.0
                self.egg_bsod_entered = False
                self.egg_bsod_glitch_t = 0.0

        elif self.egg_phase == "bsod":
            # One-shot BSOD shock sound + volume peak
            if not self.egg_bsod_entered:
                self.egg_bsod_entered = True
                self.sounds.play("bsod_shock")
                if self.egg_noise_channel is not None:
                    try:
                        self.egg_noise_channel.set_volume(1.0)
                    except Exception:
                        pass
            self.egg_fx_strength = 1.0
            # Occasional crackle
            self.egg_glitch_sound_timer -= dt
            if self.egg_glitch_sound_timer <= 0:
                self.sounds.play(random.choice(["static_crackle", "glitch"]))
                self.egg_glitch_sound_timer = random.uniform(0.18, 0.45)
            # Exit after BSOD hold time
            if self.egg_timer >= 5.0:
                self.sounds.stop_channel(self.egg_noise_channel)
                self.egg_noise_channel = None
                self.running = False
                return

        # ── Volume ramp (peaks at BSOD) ──────────────────────────────────────
        if self.egg_phase == "bsod":
            target_volume = 1.0
        elif self.egg_phase == "chaos":
            t_ramp = clamp(self.egg_timer / 3.8, 0.0, 1.0)
            target_volume = 0.55 + 0.45 * (t_ramp ** 0.8)
        else:
            total_ramp = clamp(self.egg_total_timer / 16.0, 0.0, 1.0)
            target_volume = 0.028 + (0.52 * (total_ramp ** 1.3)) + (0.12 * self.egg_fx_strength)

        if self.egg_noise_channel is not None:
            try:
                self.egg_noise_channel.set_volume(clamp(target_volume, 0.0, 1.0))
            except Exception:
                pass

    def _draw_matrix_rain(self, surf: pygame.Surface):
        char_h = getattr(self, "egg_char_h", 12)
        phase  = getattr(self, "egg_phase", "matrix_intro")
        for col in self.egg_matrix_cols:
            x      = col["x"]
            head_y = int(col["head_y"])
            chars  = col["chars"]
            length = col["length"]
            tint   = col.get("tint", 0)  # 0=classic green, 1=cyan-green, 2=pale lime

            for j, ch in enumerate(chars):
                y = head_y - j * char_h
                if not (-char_h <= y < HEIGHT):
                    continue

                if j == 0:
                    # ── Glowing head character ──────────────────────────────
                    # Inner bloom: draw slightly blurred copies around it
                    glow_col = (0, 200, 90) if tint != 1 else (0, 200, 180)
                    for gx, gy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)):
                        draw_text(surf, self.font_small, ch, (x + gx, y + gy), glow_col, shadow=False)
                    color = (235, 255, 240) if tint == 0 else (220, 255, 255) if tint == 1 else (240, 255, 210)
                elif j <= 2:
                    if tint == 1:
                        color = (0, 255, 175)
                    elif tint == 2:
                        color = (120, 255, 100)
                    else:
                        color = (0, 255, 90)
                elif j <= 6:
                    if tint == 1:
                        color = (0, 210, 135)
                    else:
                        color = (0, 210, 68)
                elif j <= 14:
                    fade = max(40, 195 - j * 9)
                    if tint == 2:
                        color = (0, fade, int(fade * 0.25))
                    elif tint == 1:
                        color = (0, fade, int(fade * 0.55))
                    else:
                        color = (0, fade, 0)
                else:
                    fade = max(14, 130 - (j - 14) * 6)
                    color = (0, fade, 0)

                draw_text(surf, self.font_small, ch, (x, y), color, shadow=False)

                # Ghost echo on adjacent pixel for depth (only mid-trail)
                if 1 <= j <= 5 and random.random() < 0.20:
                    ghost_c = (0, max(12, color[1] - 70), 0)
                    draw_text(surf, self.font_small, ch, (x + 1, y + 1), ghost_c, shadow=False)

                # In glitch/chaos/bsod: occasional red or white flash chars
                if phase in ("glitch_text", "chaos", "bsod") and random.random() < 0.06:
                    flash_c = random.choice([(255, 0, 60), (255, 255, 255), (80, 255, 200)])
                    draw_text(surf, self.font_small, ch, (x, y), flash_c, shadow=False)

    def _egg_scanline_strength(self) -> float:
        return clamp(0.22 + self.egg_fx_strength * 0.60, 0.22, 1.0)

    def _draw_egg_scanlines(self, surf: pygame.Surface):
        strength = self._egg_scanline_strength()
        scan = get_clear_surface((WIDTH, HEIGHT), ("egg_scanlines", self.egg_phase or "none"))
        # Primary scanlines every 2px
        for y in range(0, HEIGHT, 2):
            base_a = 12 if y % 4 else 22
            alpha  = int(clamp(base_a * strength, 0, 255))
            pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (WIDTH, y), 1)
        # Fine bright lines every 6px for CRT glow feel
        for y in range(0, HEIGHT, 6):
            alpha = int(clamp(6 * strength, 0, 40))
            pygame.draw.line(scan, (80, 255, 130, alpha), (0, y), (WIDTH, y), 1)
        # Slow-scrolling thick dark band
        band_y = int((self.egg_total_timer * 38) % HEIGHT)
        for dy in range(12):
            a = int(clamp((18 - dy * 1.2) * strength, 0, 255))
            yy = (band_y + dy) % HEIGHT
            pygame.draw.line(scan, (0, 0, 0, a), (0, yy), (WIDTH, yy), 1)
        surf.blit(scan, (0, 0))

    def _draw_egg_vcr_distortion(self, surf: pygame.Surface):
        strength = self.egg_fx_strength
        if strength <= 0.02:
            return
        base = surf.copy()
        t    = self.egg_total_timer

        # ── Jitter / shake ────────────────────────────────────────────────
        jitter_x = int(math.sin(t * 27.0) * (3 + strength * 10) + random.randint(-2, 2) * strength)
        jitter_y = int(math.sin(t * 19.0) * (1 + strength * 4))
        if abs(jitter_x) > 0 or abs(jitter_y) > 0:
            surf.blit(base, (jitter_x, jitter_y))

        # ── Horizontal scan-band tears ────────────────────────────────────
        band_count = int(6 + strength * 18)
        for i in range(band_count):
            band_y = int((t * (68 + i * 5) + i * 67) % HEIGHT)
            band_h = 3 + (i % 4) * 5
            band   = pygame.Rect(0, band_y, WIDTH, min(band_h, HEIGHT - band_y))
            if band.height <= 0:
                continue
            try:
                sl = base.subsurface(band).copy()
            except Exception:
                continue
            shift = int(math.sin(t * 7.0 + i * 1.6) * (8 + strength * 32))
            surf.blit(sl, (shift, band_y))

        # ── RGB channel split (chromatic aberration) ──────────────────────
        if strength > 0.28:
            split_amt = int(strength * 14)
            # Red channel shifted left
            r_surf = get_clear_surface((WIDTH, HEIGHT), ("egg_rgb_split_r", int(strength * 100)))
            r_surf.blit(base, (0, 0))
            r_arr = pygame.surfarray.pixels3d(r_surf)
            r_arr[:, :, 1] = 0
            r_arr[:, :, 2] = 0
            del r_arr
            surf.blit(r_surf, (-split_amt, 0), special_flags=pygame.BLEND_RGB_ADD)
            # Blue channel shifted right
            b_surf = get_clear_surface((WIDTH, HEIGHT), ("egg_rgb_split_b", int(strength * 100)))
            b_surf.blit(base, (0, 0))
            b_arr = pygame.surfarray.pixels3d(b_surf)
            b_arr[:, :, 0] = 0
            b_arr[:, :, 1] = 0
            del b_arr
            surf.blit(b_surf, (split_amt, 0), special_flags=pygame.BLEND_RGB_ADD)

        # ── White flash streaks ────────────────────────────────────────────
        for _ in range(int(4 + strength * 12)):
            fy = random.randint(0, HEIGHT - 2)
            fh = random.randint(1, 4)
            fa = int(clamp(14 * strength, 0, 80))
            pygame.draw.rect(surf, (255, 255, 255, fa), (0, fy, WIDTH, fh))

    def _draw_egg_glitch_noise(self, surf: pygame.Surface):
        strength = self.egg_fx_strength
        if strength <= 0.05:
            return
        noise = get_clear_surface((WIDTH, HEIGHT), ("egg_noise", int(strength * 100)))

        # Fine pixel noise
        speck_count = int(1600 + strength * 3800)
        for _ in range(speck_count):
            nx = random.randrange(WIDTH)
            ny = random.randrange(HEIGHT)
            c  = random.choice(((0, 255, 80), (255, 255, 255), (0, 180, 60),
                                (255, 60, 110), (0, 220, 180), (255, 220, 0)))
            na = random.randint(10, int(42 + strength * 100))
            noise.set_at((nx, ny), (*c, na))
        surf.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Macro pixel-block glitches in chaos/bsod
        if strength > 0.65:
            block_count = int(strength * 14)
            for _ in range(block_count):
                bx = random.randint(0, WIDTH - 40)
                by = random.randint(0, HEIGHT - 20)
                bw = random.randint(8, 60)
                bh = random.randint(2, 18)
                bc = random.choice([(0, 255, 80), (255, 0, 80), (255, 255, 0),
                                    (0, 80, 255), (255, 255, 255), (80, 0, 0)])
                ba = random.randint(30, 120)
                block = get_clear_surface((bw, bh), ("egg_block", bw, bh, bc, ba))
                block.fill((*bc, ba))
                surf.blit(block, (bx, by))

    def draw_matrix_egg(self):
        surf = self.screen

        # ── BSOD phase: completely separate rendering ─────────────────────
        if self.egg_phase == "bsod":
            # Hard blue fill — classic BSOD colour
            surf.fill((0, 0, 170))
            jx = random.randint(-2, 2) if self.egg_timer < 0.25 else 0

            # Title bar
            bar_rect = pygame.Rect(36, 54, WIDTH - 72, 34)
            pygame.draw.rect(surf, (255, 255, 255), bar_rect)
            pygame.draw.rect(surf, (0, 0, 170), bar_rect.inflate(-6, -6))
            draw_text(surf, self.font_big, "Windows", (WIDTH // 2 + jx, 71),
                      (255, 255, 255), center=True, shadow=False)

            bsod_body = [
                "A fatal exception 0E has occurred at 0028:C0011E36 in VXD VMM(01)+",
                "00003A1. The current application will be terminated.",
                "",
                "* Press any key to terminate the current application.",
                "* Press CTRL+ALT+DEL to restart your computer. You will",
                "  lose any unsaved information in all applications.",
                "",
                "",
                "Press any key to continue _" if int(self.egg_timer * 2) % 2 == 0 else "Press any key to continue  ",
            ]
            y0 = 108
            for i, line in enumerate(bsod_body):
                # Occasional bit-flip corruption on a random char
                if line and random.random() < 0.04:
                    p = random.randint(0, len(line) - 1)
                    line = line[:p] + random.choice("█▓▒░@#%?") + line[p + 1:]
                draw_text(surf, self.font_small, line,
                          (56 + jx, y0 + i * 22), (255, 255, 255), shadow=False)

            # Blinking block cursor at bottom
            if int(self.egg_timer * 2) % 2 == 0:
                pygame.draw.rect(surf, (255, 255, 255),
                                 (56, y0 + len(bsod_body) * 22, 10, 17))

            # BSOD scanlines
            self._draw_egg_scanlines(surf)
            # Random horizontal tear at start shock
            if self.egg_timer < 0.6 or random.random() < 0.18:
                for _ in range(random.randint(2, 8)):
                    ty = random.randint(0, HEIGHT - 4)
                    th = random.randint(1, 5)
                    to = random.randint(-45, 45)
                    try:
                        sl = surf.subsurface(pygame.Rect(0, ty, WIDTH, min(th, HEIGHT - ty))).copy()
                        surf.blit(sl, (to, ty))
                    except Exception:
                        pass
            return  # ← skip matrix rain / normal post-processing

        # ── All other phases: black + matrix rain base ────────────────────
        surf.fill((0, 0, 0))
        self._draw_matrix_rain(surf)

        # ── Phase-specific overlays ───────────────────────────────────────
        if self.egg_phase == "messages" and self.egg_msg_index < len(EGG_MESSAGES):
            raw     = EGG_MESSAGES[self.egg_msg_index]
            visible = raw[: self.egg_type_chars]
            glitched = "".join(
                random.choice("!@#$%^&*01?ｱｲｳｴｵ") if random.random() < 0.11 else c
                for c in visible
            )
            if self.egg_type_chars < len(raw):
                cursor  = "█" if int(self.egg_timer * 7) % 2 == 0 else " "
                glitched += cursor

            # Dark frosted backing
            bw = min(WIDTH - 40, max(120, len(glitched) * 14 + 70))
            backing = pygame.Surface((bw, 64), pygame.SRCALPHA)
            backing.fill((0, 0, 0, 210))
            pygame.draw.rect(backing, (0, 255, 80, 30), backing.get_rect(), border_radius=6)
            surf.blit(backing, (WIDTH // 2 - bw // 2, HEIGHT // 2 - 32))

            # Chromatic aberration on message text (red/blue ghost layers)
            for dx, dy, col in ((-3, 0, (255, 0, 60)), (3, 0, (0, 100, 255)), (0, 0, (0, 255, 70))):
                draw_text(surf, self.font_big, glitched,
                          (WIDTH // 2 + dx + random.randint(-2, 2),
                           HEIGHT // 2 + dy),
                          col, center=True, shadow=False)

            # Blinking prompt line
            if int(self.egg_timer * 3) % 2 == 0:
                draw_text(surf, self.font_small, "> SYSTEM RUNNING...",
                          (WIDTH // 2, HEIGHT // 2 + 38), (0, 180, 50), center=True, shadow=False)

        elif self.egg_phase == "pause":
            # Minimal: pulsing green underscore in centre
            if int(self.egg_total_timer * 5) % 2 == 0:
                draw_text(surf, self.font_big, "_",
                          (WIDTH // 2, HEIGHT // 2), (0, 255, 70), center=True, shadow=False)

        elif self.egg_phase == "glitch_text":
            base = EGG_GLITCH_TEXT
            # Heavy corruption
            glitched = "".join(
                random.choice("!@#$%^&*<>{}[]|\\?/~`0123456789ｱｲｳｴｵｶｷｸｹｺ") if random.random() < 0.52 else c
                for c in base
            )
            # Triple-layer chromatic aberration
            for dx, dy, col in ((-7, -4, (255, 0, 60)),
                                 (7,  4, (0, 80, 255)),
                                 (-2,  2, (0, 255, 0)),
                                 (0,  0, (0, 255, 70))):
                draw_text(surf, self.font,
                          glitched,
                          (WIDTH // 2 + dx + random.randint(-15, 15),
                           HEIGHT // 2 + dy + random.randint(-10, 10)),
                          col, center=True, shadow=False)
            # Flicker secondary line
            if random.random() < 0.22:
                draw_text(surf, self.font_small, "VCR TRACKING LOST",
                          (WIDTH // 2, HEIGHT // 2 + 46), (255, 255, 255), center=True, shadow=False)
            if random.random() < 0.18:
                draw_text(surf, self.font_small, "SIGNAL CORRUPTED",
                          (WIDTH // 2, HEIGHT // 2 - 46), (255, 0, 60), center=True, shadow=False)

        elif self.egg_phase == "chaos":
            # ── Full green-tinted noise base ───────────────────────────────
            arr = np.random.randint(0, 256, (HEIGHT, WIDTH, 3), dtype=np.uint8)
            arr[:, :, 1] = np.clip(arr[:, :, 1].astype(np.int32) + 130, 0, 255).astype(np.uint8)
            arr[:, :, 0] = np.clip(arr[:, :, 0].astype(np.int32) + 18, 0, 255).astype(np.uint8)
            arr[:, :, 2] = np.clip(arr[:, :, 2].astype(np.int32) - 30, 0, 255).astype(np.uint8)
            noise_surf = pygame.surfarray.make_surface(arr.swapaxes(0, 1))
            surf.blit(noise_surf, (0, 0))

            # ── Aggressive horizontal tearing ──────────────────────────────
            for _ in range(55):
                sy  = random.randint(0, HEIGHT - 14)
                sh  = random.randint(2, 28)
                off = random.randint(-200, 200)
                region = pygame.Rect(0, sy, WIDTH, min(sh, HEIGHT - sy))
                try:
                    sl = surf.subsurface(region).copy()
                    surf.blit(sl, (off, sy))
                except Exception:
                    pass

            # ── Scrolling hex-dump text ────────────────────────────────────
            hex_chars  = "0123456789ABCDEF"
            hex_scroll = int(getattr(self, "egg_hex_offset", 0))
            for row in range(0, HEIGHT + 18, 18):
                ry = (row - hex_scroll % HEIGHT)
                line = "".join(random.choice(hex_chars) for _ in range(WIDTH // 8 + 1))
                draw_text(surf, self.font_small, line, (0, ry),
                          (0, random.randint(160, 255), 0), shadow=False)

            # ── Pixel sparks ───────────────────────────────────────────────
            for sp in self.egg_pixel_sparks:
                t_frac = 1.0 - sp["life"] / sp["max_life"]
                a_frac = sp["life"] / sp["max_life"]
                c = sp["c"]
                sz = max(1, int(sp["sz"] * a_frac))
                pygame.draw.rect(surf, c, (int(sp["x"]), int(sp["y"]), sz, sz))

            # ── Error word scattering ──────────────────────────────────────
            error_words = [
                "ERROR", "CORRUPT", "0xDEAD", "SEGFAULT", "NULL", "OVERFLOW",
                "KERNEL PANIC", "FATAL", "0xFF", "STACK SMASH", "GLITCH",
                "SYNC LOST", "ACCESS VIOLATION", "HEAP DUMP", "INT 3",
                "0x00000000", "PAGE FAULT", "EXCEPTION", "!!!",
            ]
            for _ in range(40):
                word = random.choice(error_words)
                ex   = random.randint(0, WIDTH - 1)
                ey   = random.randint(0, HEIGHT - 1)
                ec   = (random.randint(80, 255), random.randint(0, 255), random.randint(0, 120))
                draw_text(surf, self.font_small, word, (ex, ey), ec, shadow=False)

            # ── SYSTEM CRASH banner ────────────────────────────────────────
            if random.random() < 0.55:
                bw = WIDTH - 60
                banner = pygame.Surface((bw, 52), pygame.SRCALPHA)
                banner.fill((0, 0, 0, 200))
                surf.blit(banner, (30, HEIGHT // 2 - 26))
                glitch_title = "".join(
                    random.choice("!#%@*?░▒▓") if random.random() < 0.35 else c
                    for c in ">>> SYSTEM FAILURE <<<"
                )
                for dxdy, col in (((-5, -2), (255, 0, 60)), ((5, 2), (0, 80, 255)),
                                  ((0, 0), (0, 255, 60))):
                    draw_text(surf, self.font_big, glitch_title,
                              (WIDTH // 2 + dxdy[0] + random.randint(-8, 8),
                               HEIGHT // 2 + dxdy[1] + random.randint(-6, 6)),
                              col, center=True, shadow=False)

        # ── Shared post-processing ────────────────────────────────────────
        self._draw_egg_scanlines(surf)
        self._draw_egg_vcr_distortion(surf)
        self._draw_egg_glitch_noise(surf)

    def update_menu_ambient(self, dt: float):
        self.menu_scroll += dt
        for cloud in self.clouds:
            cloud.update(dt * 0.45)
        retain_clouds(self.clouds)
        while len(self.clouds) < 7:
            self.clouds.append(Cloud(WIDTH + random.uniform(0, 160), random.uniform(40, 260), random.uniform(0.6, 1.4), random.uniform(8, 22), random.randint(0, 2)))
        for p in self.particles:
            p.update(dt)
        retain_positive_life(self.particles)
        if random.random() < 0.04:
            self.add_particle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), random.uniform(-8, -2), random.uniform(10, 30), 1.2, 2, (255, 255, 255))
        for t in self.texts:
            t.update(dt)
        retain_positive_life(self.texts)

    # ── Letterbox / scaling helpers ───────────────────────────────────────────

    def _game_rect(self) -> pygame.Rect:
        """Return the letterboxed game area (aspect-ratio-correct) inside the real window."""
        ww, wh = self._window.get_size()
        current_size = (ww, wh)
        if self._cached_game_rect_size == current_size:
            return self._cached_game_rect

        scale = min(ww / WIDTH, wh / HEIGHT)
        sw, sh = max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale))
        ox, oy = (ww - sw) // 2, (wh - sh) // 2
        self._cached_game_rect = pygame.Rect(ox, oy, sw, sh)
        self._cached_game_rect_size = current_size
        return self._cached_game_rect

    def _remap_mouse_event(self, event: pygame.event.Event) -> pygame.event.Event:
        """Translate a mouse event's position from window coords → game coords."""
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            return event
        rect = self._game_rect()
        if rect.width == 0 or rect.height == 0:
            return event
        raw = event.pos
        gx = int((raw[0] - rect.x) * WIDTH / rect.width)
        gy = int((raw[1] - rect.y) * HEIGHT / rect.height)
        d = {**event.__dict__, "pos": (gx, gy)}
        return pygame.event.Event(event.type, d)

    def _game_mouse_pos(self) -> Tuple[int, int]:
        """Return current mouse position mapped to game (960×540) coordinates."""
        rect = self._game_rect()
        raw = pygame.mouse.get_pos()
        if rect.width == 0 or rect.height == 0:
            return raw
        gx = int((raw[0] - rect.x) * WIDTH / rect.width)
        gy = int((raw[1] - rect.y) * HEIGHT / rect.height)
        return (gx, gy)

    def _toggle_fullscreen(self):
        """Toggle between resizable-windowed and borderless fullscreen."""
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self._window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self._window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self._cached_game_rect_size = None

    def main_loop(self):
        self.reset_world()
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1.0 / 45.0)
            if self.state == "PLAY" and hasattr(self, "time_scale"):
                dt *= self.time_scale

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue

                # ── F11: toggle fullscreen ────────────────────────────────
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                    continue

                # ── Remap mouse positions from window space → game space ──
                event = self._remap_mouse_event(event)

                # ── Easter egg: bấm 3 GIỮ rồi bấm 6 (đúng thứ tự, không nhớ sau khi nhả) ──
                if self.state not in ("PLAY", "PAUSE", "GAME_OVER", "CLEAR", "MATRIX_EGG"):
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_6:
                        pressed = pygame.key.get_pressed()
                        if pressed[pygame.K_3]:
                            self._start_matrix_egg()
                            continue
                    if self.state == "MENU":
                        self.handle_menu_event(event)
                    elif self.state == "SKINS":
                        self.handle_skin_event(event)
                    elif self.state == "DIFFICULTY":
                        self.handle_difficulty_event(event)
                    elif self.state == "BOSS_SELECT":
                        self.handle_boss_select_event(event)
                    elif self.state == "OPTIONS":
                        self.handle_options_event(event)
                    elif self.state == "PROFILE":
                        self.handle_profile_event(event)
                elif self.state in ("PLAY", "PAUSE", "GAME_OVER", "CLEAR"):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state in ("PLAY", "PAUSE"):
                        if self.click_pause_toggle_button(event.pos):
                            self.sounds.play("click")
                            continue
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                        self.set_sound_enabled(not self.sound_on)
                        self.message = "Sound On" if self.sound_on else "Sound Off"
                        self.message_timer = 0.9
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes
                        self.save_settings()
                    if self.state == "PAUSE":
                        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
                            self.state = "PLAY"
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self.click_pause_toggle_button(event.pos):
                                self.sounds.play("click")
                            else:
                                self.click_pause_button(event.pos)
                    elif self.state == "PLAY":
                        self.handle_play_event(event)
                    elif self.state == "GAME_OVER":
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
                            elif event.key == pygame.K_ESCAPE:
                                self.state = "MENU"
                                self.save_settings()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.click_game_over_button(event.pos)
                    elif self.state == "CLEAR":
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                self.start_game(self.current_mode, self.current_difficulty_index, self.boss_index)
                            elif event.key == pygame.K_ESCAPE:
                                self.state = "MENU"
                                self.save_settings()
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.click_clear_button(event.pos)

            self.update_button_fx(dt)
            self.update_notifications(dt)
            if self.state == "MATRIX_EGG":
                self.update_matrix_egg(dt)
                self.draw_matrix_egg()
            elif self.state == "MENU":
                self.update_menu_ambient(dt)
                self.draw_menu()
            elif self.state == "SKINS":
                self.update_menu_ambient(dt)
                self.draw_skin_screen()
            elif self.state == "DIFFICULTY":
                self.update_menu_ambient(dt)
                self.draw_difficulty_screen()
            elif self.state == "BOSS_SELECT":
                self.update_menu_ambient(dt)
                self.draw_boss_select_screen()
            elif self.state == "OPTIONS":
                self.update_menu_ambient(dt)
                self.draw_options_screen()
            elif self.state == "PROFILE":
                self.update_menu_ambient(dt)
                self.draw_profile_screen()
            elif self.state == "PLAY":
                self.update_play(dt)
                self.draw_play()
            elif self.state == "PAUSE":
                self.draw_pause()
            elif self.state == "GAME_OVER":
                self.draw_play()
            elif self.state == "CLEAR":
                self.draw_play()

            # ── Letterbox blit: avoid rescaling when the window is already native ──
            grect = self._game_rect()
            self._window.fill((0, 0, 0))
            if grect.size == self.screen.get_size():
                self._window.blit(self.screen, grect.topleft)
            else:
                scaled = pygame.transform.scale(self.screen, grect.size)
                self._window.blit(scaled, grect.topleft)
            pygame.display.flip()

            # Save any pending settings in the background between frames.
            self._flush_settings_save()

        self.save_settings(force=True)
        pygame.quit()

if __name__ == "__main__":
    Game().main_loop()
