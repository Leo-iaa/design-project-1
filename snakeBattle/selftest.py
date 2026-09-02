#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selftest.py —— 开发自测脚本（不属于游戏本体，交付前可删）

在无窗口（headless）模式下验证对战规则和 AI 行为：
    python selftest.py

覆盖用例：
  A. 碰撞判定：撞墙 / 撞自己 / 追尾巴合法 / 头对头 / 对穿 / 撞对方身体 /
     会死的蛇尾巴不腾空 / 别人的尾巴腾空可进
  B. 计分与胜负：吃食物加分变长 / 吃满目标分获胜 / 死亡判负 / 死蛇不吃食物
  C. AI：单蛇独走不吃库 / 不反向 / 1v1 完整对局能赢直行玩家 / 长局缠斗能吃满
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()

from config import TARGET_SCORE, UP, DOWN, LEFT, RIGHT, GRID_WIDTH
from game import Game, MODE_AI, MODE_PVP
from snake import Snake

PASSED = 0


def check(name: str, cond: bool) -> None:
    global PASSED
    PASSED += 1
    print(("[通过] " if cond else "[失败] ") + name)
    assert cond, "自测失败: " + name


def mk(name: str, positions: list[tuple[int, int]], direction: tuple[int, int]) -> Snake:
    """构造一条指定身体和方向的蛇（测试用，绕过出生逻辑）。"""
    s = Snake(name, positions[0], direction, (0, 255, 0), (0, 150, 0))
    s.positions = list(positions)
    return s


def fresh_game(mode: str = MODE_AI) -> Game:
    g = Game(mode, headless=True)
    g.snakes = []
    g.foods.positions = []
    g.game_over = False
    return g


def run_ticks(g: Game, n: int) -> None:
    for _ in range(n):
        g.update()
        if g.game_over:
            return


# ================= A. 碰撞判定 =================
print("---- A. 碰撞判定 ----")

# A1 撞墙
g = fresh_game()
a = mk("你", [(0, 5), (1, 5), (2, 5)], LEFT)
b = mk("电脑", [(30, 24), (31, 24), (32, 24)], LEFT)
g.snakes = [a, b]
g.update()
check("A1 撞墙死亡", not a.alive and b.alive and g.game_over and g.result_text == "电脑 获胜！")

# A2 撞自己身体
g = fresh_game()
a = mk("你", [(10, 10), (11, 10), (12, 10)], RIGHT)  # 前方就是自己的脖子
b = mk("电脑", [(30, 24), (31, 24), (32, 24)], LEFT)
g.snakes = [a, b]
g.update()
check("A2 撞自己身体死亡", not a.alive and b.alive)

# A3 紧贴自己尾巴走（尾巴腾空）合法
g = fresh_game()
a = mk("你", [(10, 10), (10, 11), (10, 12)], UP)  # 新头(10,9)；尾巴(10,12)会腾空
b = mk("电脑", [(20, 20), (21, 20), (22, 20)], LEFT)
g.snakes = [a, b]
g.update()
check("A3 追自己尾巴不死", a.alive and a.head() == (10, 9) and len(a.positions) == 3)

# A4 头对头：新头同格 -> 双双死 -> 平局
g = fresh_game()
a = mk("你", [(10, 10), (9, 10), (8, 10)], RIGHT)
b = mk("电脑", [(12, 10), (13, 10), (14, 10)], LEFT)
g.snakes = [a, b]
g.update()
check("A4 头对头同归于尽判平局", (not a.alive and not b.alive
                          and g.game_over and g.result_text == "平局！"))

# A5 对穿：互换成对方旧头位置 -> 双双死
g = fresh_game()
a = mk("你", [(10, 10), (9, 10), (8, 10)], RIGHT)
b = mk("电脑", [(11, 10), (12, 10), (13, 10)], LEFT)
g.snakes = [a, b]
g.update()
check("A5 对穿同归于尽判平局", not a.alive and not b.alive and g.result_text == "平局！")

# A6 撞对方身体 -> 撞的人死
g = fresh_game()
a = mk("你", [(10, 10), (9, 10), (8, 10)], RIGHT)          # 新头(11,10)
b = mk("电脑", [(11, 10), (11, 9), (11, 8)], DOWN)          # 身体在头后方，占着(11,10)
g.snakes = [a, b]
g.update()
check("A6 撞对方身体死亡", not a.alive and b.alive and g.result_text == "电脑 获胜！")

# A7 会死的蛇：尾巴这步不腾空（撞上它尾巴也算撞）
g = fresh_game()
a = mk("你", [(GRID_WIDTH - 1, 15), (GRID_WIDTH - 2, 15), (GRID_WIDTH - 3, 15)], RIGHT)  # 撞墙
b = mk("电脑", [(GRID_WIDTH - 3, 16), (GRID_WIDTH - 3, 17), (GRID_WIDTH - 3, 18)], UP)   # 头撞 a 的尾巴
g.snakes = [a, b]
g.update()
check("A7 死蛇尾巴不腾空", not a.alive and not b.alive and g.result_text == "平局！")

# A8 别人的尾巴腾空可以进（那条蛇没死也没吃）
g = fresh_game()
a = mk("你", [(10, 10), (10, 11), (10, 12)], UP)     # 尾巴(10,12)将腾空
b = mk("电脑", [(10, 13), (10, 14), (10, 15)], UP)   # 新头(10,12)
g.snakes = [a, b]
g.update()
check("A8 进别人腾空的尾巴格合法", a.alive and b.alive and b.head() == (10, 12))

# ================= B. 计分与胜负 =================
print("---- B. 计分与胜负 ----")

# B1 吃食物：加分、变长、补食物且不刷在蛇身上
g = fresh_game()
a = mk("你", [(10, 10), (9, 10), (8, 10)], RIGHT)
b = mk("电脑", [(30, 24), (31, 24), (32, 24)], LEFT)
g.snakes = [a, b]
g.foods.positions = [(11, 10)]
g.update()
check("B1 吃食物加分变长", a.score == 1 and len(a.positions) == 4 and a.head() == (11, 10))
check("B1 食物补位且避开蛇身", len(g.foods.positions) == 1
      and g.foods.positions[0] not in set(a.positions) | set(b.positions))

# B2 吃满目标分获胜
g = fresh_game()
a = mk("你", [(10, 10), (9, 10), (8, 10)], RIGHT)
b = mk("电脑", [(30, 24), (31, 24), (32, 24)], LEFT)
a.score = TARGET_SCORE - 1
g.snakes = [a, b]
g.foods.positions = [(11, 10)]
g.update()
check("B2 吃满目标分获胜", g.game_over and g.result_text == "你赢了！" and a.score == TARGET_SCORE)

# B3 死亡优先于得分：撞身体的那步即使吃到食物也不算
g = fresh_game()
a = mk("你", [(10, 10), (9, 10), (8, 10)], RIGHT)      # 新头(11,10)=食物=电脑身体
b = mk("电脑", [(11, 10), (11, 9), (11, 8)], DOWN)      # 身体在头后方，占着(11,10)
g.snakes = [a, b]
g.foods.positions = [(11, 10)]
g.update()
check("B3 死亡优先，死蛇不吃不加分", not a.alive and a.score == 0
      and (11, 10) in g.foods.positions and g.result_text == "电脑 获胜！")

# ================= C. AI 行为 =================
print("---- C. AI 行为 ----")

# C1 单条 AI 独走：10 局里至少 8 局吃满目标分（会追食物、不轻易自杀）
wins = 0
no_reverse = True
for ep in range(10):
    g = fresh_game()
    bot = mk("电脑", [(GRID_WIDTH - 6, 24), (GRID_WIDTH - 5, 24), (GRID_WIDTH - 4, 24)], LEFT)
    bot.is_ai = True
    g.snakes = [bot]
    g.foods.respawn_all(set(bot.positions))
    prev_dir = bot.direction
    for _ in range(800):
        g.update()
        d = bot.direction
        if (d[0] * -1, d[1] * -1) == prev_dir:
            no_reverse = False
        prev_dir = d
        if g.game_over:
            break
    if bot.score >= TARGET_SCORE:
        wins += 1
check("C1 AI独走10局>=8局吃满目标分", wins >= 8)
check("C2 AI从不原地掉头", no_reverse)

# C3 1v1 完整对局：玩家直行撞墙 -> 电脑获胜
g = Game(MODE_AI, headless=True)
for _ in range(500):
    g.update()
    if g.game_over:
        break
player, bot = g.snakes
check("C3 玩家撞墙后电脑获胜", g.game_over and not player.alive and bot.alive
      and g.result_text == "电脑 获胜！")

# C4 长局缠斗：玩家绕大方圈跑（25x24，贴不下出界），AI 该稳稳拿下这一局
g = Game(MODE_AI, headless=True)
player, bot = g.snakes
side = [25, 24, 25, 24]                      # 右、下、左、上各走多少步
dirs_cycle = [DOWN, LEFT, UP, RIGHT]
turn_at: dict[int, tuple[int, int]] = {}     # 拐点时刻 -> 转向
acc = 0
for i in range(4 * 40):
    acc += side[i % 4]
    turn_at[acc] = dirs_cycle[i % 4]
for t in range(3000):
    if t in turn_at:
        player.queue_turn(turn_at[t])
    g.update()
    if g.game_over:
        break
# 玩家要么被电脑耗死/撞死，要么电脑先吃满；两种都是电脑获胜
check("C4 缠斗局电脑能获胜", g.game_over and g.result_text == "电脑 获胜！")

print(f"\n全部自测通过，共 {PASSED} 项")
