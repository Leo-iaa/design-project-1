#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py —— 全局常量（屏幕、网格、颜色、方向、DQN 超参数）

依据：基于强化学习的贪吃蛇游戏 —— 软件详细设计文档 §3 配置设计。
"""

# ---------- 屏幕与网格 ----------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 30

# ---------- 方向常量（用元组表示位移，便于向量运算） ----------
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]  # 动作 0,1,2,3

# ---------- 颜色 ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)

# ---------- DQN 超参数 ----------
LEARNING_RATE = 0.001
GAMMA = 0.99           # 折扣因子
BATCH_SIZE = 64
MEMORY_CAPACITY = 10000
EPSILON_START = 1.0    # 探索起始
EPSILON_END = 0.01     # 探索下限
EPSILON_DECAY = 0.995  # 每局衰减
TARGET_UPDATE = 100    # 目标网络更新频率（步）

# ---------- 奖励塑形（文档 §5.3） ----------
REWARD_EAT = 20.0
REWARD_DEAD = -20.0
REWARD_NEAR = 1.0
REWARD_FAR = -1.0
REWARD_STALL = -0.1
REWARD_TIMEOUT = -10.0

# ---------- 防死循环 ----------
MAX_STEPS_PER_LENGTH = 100  # 每局步数上限 = 100 * (蛇长 + 1)