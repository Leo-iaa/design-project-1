#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai.py —— 简单难度的电脑蛇

思路（三句话说清）：
1. 先排除"必死"方向：撞墙、撞任何蛇的身体（含对方，尾巴按"不长大就腾空"处理）、
   以及对方蛇头旁边的格子（对方下一步可能到达，避免对撞）；
2. 剩下的安全方向里，选"离最近食物曼哈顿距离最小"的（贪心追食）；
3. 距离打平时优先保持当前方向，其次随机——避免左右抖动。

它和玩家遵守完全相同的死亡规则：不能穿墙、不能无敌、撞了照样死。
允许看全局信息（玩家位置、食物位置），但只做基础操作，不是必胜外挂。
"""

import random

from config import GRID_WIDTH, GRID_HEIGHT, DIRECTIONS


def choose_direction(snake, snakes: list, food_positions: list[tuple[int, int]]) -> tuple[int, int]:
    """为 snake 选本步方向；返回一个方向元组（可能就是当前方向=直行）。"""
    head = snake.head()

    # ---- 1. 收集危险格子 ----
    danger: set[tuple[int, int]] = set()
    for other in snakes:
        if not other.alive:
            continue
        body = set(other.positions)
        if other is snake and not snake.just_ate and len(snake.positions) > 1:
            # 自己的尾巴：这步不吃食物就会腾空，可以进
            body.discard(snake.tail())
        # 注意：别人的尾巴按危险处理（略保守，但更不容易出事）
        danger |= body
        if other is not snake:
            # 对方蛇头四邻格 = 对方下一步可能到达的格子，避开以防对撞
            ox, oy = other.head()
            for d in DIRECTIONS:
                danger.add((ox + d[0], oy + d[1]))

    # ---- 2. 筛出安全方向 ----
    candidates: list[tuple[int, int]] = []
    for d in DIRECTIONS:
        if (d[0] * -1, d[1] * -1) == snake.direction:
            continue  # 不能原地掉头
        nx, ny = head[0] + d[0], head[1] + d[1]
        if nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT:
            continue  # 撞墙
        if (nx, ny) in danger:
            continue  # 撞身体 / 可能对撞
        candidates.append(d)

    # 无路可走：保持直行，听天由命（躲不掉的死不算"自杀"）
    if not candidates or not food_positions:
        return snake.direction

    # ---- 3. 贪心追最近的食物 ----
    def dist(cell: tuple[int, int]) -> int:
        return min(abs(cell[0] - fx) + abs(cell[1] - fy) for fx, fy in food_positions)

    best = min(dist((head[0] + d[0], head[1] + d[1])) for d in candidates)
    tied = [d for d in candidates if dist((head[0] + d[0], head[1] + d[1])) == best]
    if snake.direction in tied:
        return snake.direction
    return random.choice(tied)
