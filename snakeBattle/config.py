#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py —— 多人对战版全局常量

数值来源说明：
- 格子大小、棋盘规格沿用 snakeBasic/config.py 的设置：20px 一格，40 x 30 格；
- 窗口顶部加了一条 40px 的比分条（SCORE_BAR_HEIGHT），所以窗口总高
  = 600（棋盘）+ 40（比分条）= 640。棋盘本身仍是 40 x 30 格，没有缩小。
"""

# ---------- 屏幕与网格（沿用 snakeBasic 的数值） ----------
GRID_SIZE = 20
GRID_WIDTH = 40    # = 800 // 20，和 snakeBasic 一致
GRID_HEIGHT = 30   # = 600 // 20，和 snakeBasic 一致
SCORE_BAR_HEIGHT = 40
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE                        # 800
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE + SCORE_BAR_HEIGHT   # 640
FPS = 10  # 沿用 snakeBasic 的节奏；觉得慢可以调大

# ---------- 方向常量（和 snakeRL 一致：动作用 0/1/2/3 对应四个方向） ----------
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]  # 动作 0=上 1=下 2=左 3=右

# ---------- 游戏规则 ----------
INITIAL_LENGTH = 3        # 出生长度（双方相同，保证公平）
TARGET_SCORE = 10         # 1v1：先吃满 10 个食物获胜
FOOD_COUNT_1V1 = 1        # 第一版(简单 AI)场上同时 1 个食物；以后做普通难度再调大
INPUT_QUEUE_LEN = 2       # 每条蛇的转向输入缓冲长度（允许一帧内连按两个键）
SCORE_PULSE_FRAMES = 6    # 得分数字跳动的帧数

# ---------- 颜色（沿用 snakeBasic，另加对战需要的） ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
BAR_GRAY = (25, 25, 25)     # 比分条背景

# 每条蛇的皮肤：蛇头亮色 + 蛇身暗色（预留 4 个席位，多人混战直接用）
SNAKE_SKINS = [
    {"head_color": (0, 255, 0),   "body_color": (0, 150, 0)},    # 1号：绿
    {"head_color": (255, 255, 0), "body_color": (190, 140, 0)},  # 2号：黄
    {"head_color": (0, 200, 255), "body_color": (0, 110, 150)},  # 3号：青（预留）
    {"head_color": (255, 0, 255), "body_color": (150, 0, 150)},  # 4号：紫（预留）
]
