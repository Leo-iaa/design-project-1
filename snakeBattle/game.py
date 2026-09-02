#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
game.py —— 对战主逻辑（多蛇同屏 + 碰撞判定 + 计分/胜负 + 渲染）

碰撞判定采用"同步走子"规则（对双方公平，谁也不占先手）：
1. 所有活蛇同时确定本步的新头位置；
2. 撞墙 -> 死；
3. 两蛇新头落进同一格 -> 对撞，一起死；
4. 两蛇新头互换成对方旧头的位置（对穿）-> 一起死；
5. 新头撞上"这一步走完后仍被占住的格子"（含自己的身体）-> 死。
   注意：没长大的蛇尾巴会腾空，所以紧贴着自己尾巴走是合法的；
6. 结算：1v1 / 双人模式里，一方死 -> 另一方直接获胜；同一步两边都死 -> 平局；
   先吃满 TARGET_SCORE 个食物的一方获胜（死亡判定优先于得分判定）。
"""

import pygame
import sys

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, FPS,
    SCORE_BAR_HEIGHT, TARGET_SCORE, SCORE_PULSE_FRAMES,
    UP, DOWN, LEFT, RIGHT,
    BLACK, WHITE, GRAY, RED, BAR_GRAY, SNAKE_SKINS,
)
from snake import Snake
from food import FoodManager
import ai

# 模式名
MODE_PVP = "pvp"   # 双人类对战
MODE_AI = "1v1"    # 人机对战（第一版只有简单难度）

# 键位映射：玩家1 用 WASD，玩家2 用方向键。
# 每个键除了 keycode 还配了 scancode（物理位置码）：
# 中文输入法拦截按键时 event.key 可能失效，但 event.scancode 依然可靠。
KEYMAP_P1 = {
    pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT,
    pygame.KSCAN_W: UP, pygame.KSCAN_S: DOWN, pygame.KSCAN_A: LEFT, pygame.KSCAN_D: RIGHT,
}
KEYMAP_P2 = {
    pygame.K_UP: UP, pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT,
    pygame.KSCAN_UP: UP, pygame.KSCAN_DOWN: DOWN,
    pygame.KSCAN_LEFT: LEFT, pygame.KSCAN_RIGHT: RIGHT,
}

# 中文字体候选（Windows 自带）；都没有就退回 pygame 默认字体
FONT_CANDIDATES = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]


def get_font(size: int) -> pygame.font.Font:
    """拿一个能显示中文的字体。"""
    for path in FONT_CANDIDATES:
        try:
            return pygame.font.Font(path, size)
        except Exception:
            continue
    return pygame.font.SysFont(None, size)


def make_snakes(mode: str) -> list[Snake]:
    """按模式生成蛇：对角出生、长度相同、方向朝对方半场，规则完全对称。"""
    if mode == MODE_PVP:
        return [
            Snake("玩家1", (5, 5), RIGHT, **SNAKE_SKINS[0]),
            Snake("玩家2", (GRID_WIDTH - 6, GRID_HEIGHT - 6), LEFT, **SNAKE_SKINS[1]),
        ]
    # 1v1：玩家 + 电脑
    return [
        Snake("你", (5, 5), RIGHT, **SNAKE_SKINS[0]),
        Snake("电脑", (GRID_WIDTH - 6, GRID_HEIGHT - 6), LEFT, **SNAKE_SKINS[1], is_ai=True),
    ]


class Game:
    """一局对战：管理所有蛇、食物、胜负和画面。"""

    def __init__(self, mode: str, headless: bool = False) -> None:
        self.mode = mode
        self.headless = headless
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.font_big = self.font_mid = self.font_small = None
        self.setup_round()
        if not headless:
            self._ensure_display()

    def setup_round(self) -> None:
        """开新的一局（按 R 重开也走这里）。"""
        self.snakes: list[Snake] = make_snakes(self.mode)
        occupied: set[tuple[int, int]] = set()
        for s in self.snakes:
            occupied |= set(s.positions)
        self.foods = FoodManager()
        self.foods.respawn_all(occupied)
        self.game_over = False
        self.back_to_menu = False
        self.result_text = ""
        # 得分跳动动画：snake.name -> 剩余帧数
        self.pulse: dict[str, int] = {s.name: 0 for s in self.snakes}

    # ---------------- 窗口 ----------------

    def _ensure_display(self) -> None:
        """惰性建窗口（headless 模式永不调用，方便自动化测试）。"""
        if self.screen is not None:
            return
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇对战")
        # 防止中文输入法吞字母键（详见 main.py 里的注释）
        pygame.key.stop_text_input()
        self.clock = pygame.time.Clock()
        self.font_big = get_font(40)
        self.font_mid = get_font(28)
        self.font_small = get_font(20)

    # ---------------- 输入 ----------------

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.scancode == pygame.KSCAN_ESCAPE:
                    # 对局中按 ESC：回菜单
                    self.back_to_menu = True
                    continue
                if event.key == pygame.K_m or event.scancode == pygame.KSCAN_M:
                    self.back_to_menu = True
                    continue
                if ((event.key == pygame.K_r or event.scancode == pygame.KSCAN_R)
                        and self.game_over):
                    self.setup_round()
                    continue
                if self.game_over:
                    continue
                # 转向输入分发给对应的人类玩家
                # 先按 event.key 匹配；被输入法拦截时 key 失效，再按物理扫描码兜底
                keymaps = [KEYMAP_P1, KEYMAP_P2]
                humans = [s for s in self.snakes if not s.is_ai]
                for i, s in enumerate(humans):
                    d = keymaps[i].get(event.key) or keymaps[i].get(event.scancode)
                    if d is not None:
                        s.queue_turn(d)

    # ---------------- 逻辑更新（核心） ----------------

    def update(self) -> None:
        if self.game_over:
            return

        # 0) 电脑蛇先想好这一步往哪走
        for s in self.snakes:
            if s.is_ai and s.alive:
                s.queue_turn(ai.choose_direction(s, self.snakes, self.foods.positions))

        # 1) 应用输入缓冲，算出每条活蛇的新头位置
        acting = [s for s in self.snakes if s.alive]
        for s in acting:
            s.apply_pending()
        new_heads: dict[str, tuple[int, int]] = {s.name: s.compute_new_head() for s in acting}

        # 2) 这一步会不会吃到食物（决定尾巴腾不腾空）
        food_set = set(self.foods.positions)
        will_grow: dict[str, bool] = {s.name: (new_heads[s.name] in food_set) for s in acting}

        # 3) 碰撞判定（全部基于本步开始时的局面，双方同时生效）
        dead: set[str] = set()

        # 3.1 撞墙
        for s in acting:
            x, y = new_heads[s.name]
            if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                dead.add(s.name)

        # 3.2 "这步走完后仍被占住的格子"：所有活蛇的身体，
        #     只有"没长大的蛇的尾巴"会腾空；本步会死掉的蛇尾巴也不腾（它没走成）。
        occupied: set[tuple[int, int]] = set()
        for s in self.snakes:
            if not s.alive:
                continue  # 死蛇尸体不挡路
            body = set(s.positions)
            if s.name not in dead and not will_grow.get(s.name, False):
                body.discard(s.tail())
            occupied |= body

        # 3.3 头对头（新头同格）与 3.4 对穿（互换成对方旧头位置）
        old_heads = {s.name: s.head() for s in acting}
        names = [s.name for s in acting]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                ni, nj = names[i], names[j]
                if new_heads[ni] == new_heads[nj]:
                    dead.add(ni)
                    dead.add(nj)
                elif new_heads[ni] == old_heads[nj] and new_heads[nj] == old_heads[ni]:
                    dead.add(ni)
                    dead.add(nj)

        # 3.5 撞身体（别人的或自己的；"即将腾空的尾巴"不在 occupied 里，撞上不算死）
        for s in acting:
            if s.name in dead:
                continue
            if new_heads[s.name] in occupied:
                dead.add(s.name)

        # 4) 幸存者前进；死蛇标记死亡
        eaten: list[tuple[int, int]] = []
        for s in acting:
            if s.name in dead:
                s.alive = False
                continue
            nh = new_heads[s.name]
            s.advance(nh, will_grow[s.name])
            if will_grow[s.name]:
                s.score += 1
                self.pulse[s.name] = SCORE_PULSE_FRAMES
                eaten.append(nh)

        # 5) 被吃掉的食物补新的（避开蛇身和剩余食物）
        if eaten:
            occupied_now: set[tuple[int, int]] = set()
            for s in self.snakes:
                if s.alive:
                    occupied_now |= set(s.positions)
            for pos in eaten:
                self.foods.remove(pos, occupied_now)

        # 6) 结算胜负：死亡判定优先，其次看是否吃满目标分数
        def result_for(winner: Snake) -> str:
            return "你赢了！" if winner.name == "你" else f"{winner.name} 获胜！"

        dead_snakes = [s for s in acting if s.name in dead]
        if dead_snakes:
            self.game_over = True
            survivors = [s for s in self.snakes if s.alive]
            # 两条都死 -> 平局；只剩一条 -> 它获胜
            self.result_text = result_for(survivors[0]) if len(survivors) == 1 else "平局！"
        else:
            champs = [s for s in self.snakes if s.alive and s.score >= TARGET_SCORE]
            if champs:
                self.game_over = True
                # 同时吃满 -> 平局
                self.result_text = result_for(champs[0]) if len(champs) == 1 else "平局！"

    # ---------------- 绘制 ----------------

    def draw(self) -> None:
        if self.screen is None:
            return
        self.screen.fill(BLACK)
        top = SCORE_BAR_HEIGHT

        # 棋盘网格（整体下移比分条高度）
        for x in range(0, SCREEN_WIDTH + 1, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, top), (x, top + GRID_HEIGHT * GRID_SIZE))
        for y in range(GRID_HEIGHT + 1):
            yy = top + y * GRID_SIZE
            pygame.draw.line(self.screen, GRAY, (0, yy), (SCREEN_WIDTH, yy))

        # 食物和活着的蛇
        self.foods.draw(self.screen, top)
        for s in self.snakes:
            if s.alive:
                s.draw(self.screen, top)

        self._draw_score_bar()
        if self.game_over:
            self._draw_game_over()
        pygame.display.flip()

    def _draw_score_bar(self) -> None:
        """顶部比分条：你 X : Y 电脑；刚得分的数字会放大跳动。"""
        pygame.draw.rect(self.screen, BAR_GRAY, (0, 0, SCREEN_WIDTH, SCORE_BAR_HEIGHT))
        assert self.font_mid is not None and self.font_big is not None
        mid_y = SCORE_BAR_HEIGHT // 2
        center = SCREEN_WIDTH // 2

        s1, s2 = self.snakes[0], self.snakes[1]

        def seg(snake: Snake, x: int, align_right: bool) -> None:
            font = self.font_big if self.pulse[snake.name] > 0 else self.font_mid
            surf = font.render(f"{snake.name} {snake.score}", True, snake.head_color)
            rect = surf.get_rect(centery=mid_y)
            if align_right:
                rect.right = x
            else:
                rect.left = x
            self.screen.blit(surf, rect)

        seg(s1, center - 24, True)
        seg(s2, center + 24, False)
        colon = self.font_mid.render(":", True, WHITE)
        self.screen.blit(colon, colon.get_rect(center=(center, mid_y)))

        assert self.font_small is not None
        tip = self.font_small.render(f"先吃满 {TARGET_SCORE} 个食物获胜", True, GRAY)
        self.screen.blit(tip, (10, 10))

    def _draw_game_over(self) -> None:
        """结算画面：半透明遮罩 + 结果 + 操作提示。"""
        assert self.font_big is not None and self.font_mid is not None
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        mid_y = SCORE_BAR_HEIGHT + GRID_HEIGHT * GRID_SIZE // 2
        text = self.font_big.render(self.result_text, True, WHITE)
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, mid_y - 30)))
        hint = self.font_mid.render("按 R 重开    按 M 回菜单", True, GRAY)
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, mid_y + 30)))

    # ---------------- 主循环 ----------------

    def run(self) -> str:
        """主循环。返回 'menu'（回菜单）；关窗直接退出程序（snakeBasic 同款）。"""
        while True:
            self.handle_events()
            if self.back_to_menu:
                return "menu"
            self.update()
            self.draw()
            if self.clock is not None:
                self.clock.tick(FPS)
