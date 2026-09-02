#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snake.py —— 对战版 Snake 类

和 snakeBasic 的区别：
- 支持多条蛇同屏：出生位置 / 初始方向 / 颜色由外部传入；
- 转向请求先进缓冲队列（最多 INPUT_QUEUE_LEN 个），每个逻辑帧开头再应用。
  这样"一帧内连按两个键"（比如想走 上->左 的直角弯）不会丢输入，
  也不会因为原地掉头把自己撞死；
- 蛇不自己判断死活：多蛇对撞需要全局视角（谁撞谁要同时看所有蛇），
  死活判定统一放在 game.py 的 update() 里做"同步走子"结算。
"""

import pygame

from config import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT,
    INITIAL_LENGTH, INPUT_QUEUE_LEN,
    DIRECTIONS,
)


class Snake:
    """一条蛇：身体坐标（头在前）、当前方向、输入缓冲、分数、存活状态。"""

    def __init__(self, name: str, spawn: tuple[int, int], direction: tuple[int, int],
                 head_color: tuple[int, int, int], body_color: tuple[int, int, int],
                 is_ai: bool = False) -> None:
        self.name = name
        self.head_color = head_color
        self.body_color = body_color
        self.is_ai = is_ai
        self.reset(spawn, direction)

    def reset(self, spawn: tuple[int, int], direction: tuple[int, int]) -> None:
        """按出生点和初始方向重置（身体朝反方向延伸，和 snakeBasic 同款逻辑）。"""
        self.positions: list[tuple[int, int]] = [spawn]
        self.direction: tuple[int, int] = direction
        self.pending: list[tuple[int, int]] = []   # 待应用的转向请求
        self.score: int = 0                        # 吃到的食物个数
        self.alive: bool = True
        self.just_ate: bool = False                # 上一步刚吃到食物（尾巴没动）
        for i in range(1, INITIAL_LENGTH):
            self.positions.append(
                (spawn[0] - i * direction[0], spawn[1] - i * direction[1])
            )

    # ---------------- 输入 ----------------

    def queue_turn(self, new_dir: tuple[int, int]) -> None:
        """把转向请求放进缓冲队列；过滤非法输入、原地掉头和重复方向。"""
        if new_dir not in DIRECTIONS:
            return
        # 参照方向 = 队列里最后一个待应用方向；没有排队就按当前方向
        reference = self.pending[-1] if self.pending else self.direction
        if new_dir == reference:
            return                                  # 重复按同方向，忽略
        if (new_dir[0] * -1, new_dir[1] * -1) == reference:
            return                                  # 原地掉头，禁止
        if len(self.pending) < INPUT_QUEUE_LEN:
            self.pending.append(new_dir)

    def apply_pending(self) -> None:
        """每个逻辑帧开头调用：从缓冲队列取出一个转向请求应用。"""
        if self.pending:
            self.direction = self.pending.pop(0)

    # ---------------- 移动（死活判定在 game.py） ----------------

    def head(self) -> tuple[int, int]:
        return self.positions[0]

    def tail(self) -> tuple[int, int]:
        return self.positions[-1]

    def compute_new_head(self) -> tuple[int, int]:
        """只算不改：返回按当前方向走一步后的新头坐标。"""
        head = self.head()
        return (head[0] + self.direction[0], head[1] + self.direction[1])

    def advance(self, new_head: tuple[int, int], grow: bool) -> None:
        """真正前进一格。grow=True 表示这一步吃到了食物（尾巴不缩，身体变长）。"""
        self.positions.insert(0, new_head)
        if not grow:
            self.positions.pop()
        self.just_ate = grow

    # ---------------- 绘制 ----------------

    def draw(self, surface: pygame.Surface, y_offset: int = 0) -> None:
        """画蛇：头用亮色、身体用暗色。y_offset 是比分条高度（棋盘往下平移）。"""
        for i, pos in enumerate(self.positions):
            color = self.head_color if i == 0 else self.body_color
            pygame.draw.rect(
                surface, color,
                (pos[0] * GRID_SIZE, y_offset + pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )
