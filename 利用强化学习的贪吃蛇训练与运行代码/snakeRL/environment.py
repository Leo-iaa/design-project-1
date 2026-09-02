#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
environment.py —— SnakeEnv 游戏环境

依据：基于强化学习的贪吃蛇游戏 —— 软件详细设计文档 §4 游戏环境设计 (SnakeEnv)。
职责：蛇/食物状态、移动、碰撞、绘制；同时遵循强化学习环境接口 (reset / step / render)。
"""

import random
import numpy as np
import pygame

from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, FPS,
    UP, DOWN, LEFT, RIGHT, DIRECTIONS,
    BLACK, WHITE, GREEN, RED, BLUE, GRAY,
    REWARD_EAT, REWARD_DEAD, REWARD_NEAR, REWARD_FAR, REWARD_STALL, REWARD_TIMEOUT,
    MAX_STEPS_PER_LENGTH,
)


class SnakeEnv:
    """贪吃蛇游戏环境，遵循 RL 环境接口 (reset / step / render)。"""

    def __init__(self, headless: bool = True, font: pygame.font.Font | None = None):
        """
        参数:
            headless: True 时不创建 pygame 窗口；需要渲染时再调用 render() 自动 init。
            font:     共享的 pygame 字体对象（演示场景常传入）。
        """
        self.headless = headless
        self.screen = None
        self.clock = None
        # pygame.font.init() 需要 pygame.init()；headless 路径下也保持可用
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = font if font is not None else pygame.font.SysFont(None, 28)

        # 业务状态
        self.snake: list[tuple[int, int]] = []
        self.direction: tuple[int, int] = RIGHT
        self.food: tuple[int, int] = (0, 0)
        self.score: int = 0
        self.steps: int = 0
        self.alive: bool = True
        self._just_ate: bool = False

        self.reset()

    # ---------------- RL 环境接口 ----------------

    def reset(self) -> np.ndarray:
        """重置游戏环境，返回初始状态向量。"""
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.score = 0
        self.steps = 0
        self.alive = True
        self._spawn_food()
        return self._get_state()

    def step(self, action):
        """
        执行一步动作。
        action: 0=上, 1=下, 2=左, 3=右；None 表示按当前方向前进。

        返回: (next_state, reward, done)
        """
        self.steps += 1

        # 1) 计算上一步曼哈顿距离，用于距离奖励塑形
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        prev_distance = abs(food_x - head_x) + abs(food_y - head_y)

        # 2) 根据 action 修正方向（禁止直接反向）
        if action is not None:
            new_direction = DIRECTIONS[action]
            if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
                self.direction = new_direction

        # 3) 推进蛇头
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # 4) 碰撞判定：撞墙 / 撞自身（尾巴下一步会消失，故排除 tail）
        body = set(self.snake[:-1]) if not self._just_ate else set(self.snake)
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in body):
            self.alive = False
            return self._get_state(), REWARD_DEAD, True

        # 5) 更新蛇身
        self.snake.insert(0, new_head)
        self._just_ate = False

        # 6) 吃到食物判定
        if new_head == self.food:
            self.score += 1
            self._spawn_food()
            self._just_ate = True
            return self._get_state(), REWARD_EAT, False

        # 没吃到则移除尾巴
        self.snake.pop()

        # 7) 距离塑形奖励（引导智能体靠近食物）
        head_x, head_y = self.snake[0]
        new_distance = abs(food_x - head_x) + abs(food_y - head_y)
        if new_distance < prev_distance:
            reward = REWARD_NEAR
        elif new_distance > prev_distance:
            reward = REWARD_FAR
        else:
            reward = REWARD_STALL

        # 8) 防死循环超时
        if self.steps > MAX_STEPS_PER_LENGTH * (len(self.snake) + 1):
            self.alive = False
            return self._get_state(), REWARD_TIMEOUT, True

        return self._get_state(), reward, False

    def render(self, fps: int | None = None, show_info: bool = True) -> None:
        """渲染游戏画面。需要显示时调用；headless 环境会在此处惰性初始化窗口。"""
        self._ensure_display()
        self.screen.fill(BLACK)

        # 网格
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))

        # 蛇（头/死亡头/身用不同颜色）
        for i, pos in enumerate(self.snake):
            if i == 0:
                color = GREEN if self.alive else RED
            else:
                color = BLUE
            pygame.draw.rect(
                self.screen, color,
                (pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )

        # 食物
        pygame.draw.rect(
            self.screen, RED,
            (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
        )

        if show_info:
            self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (8, 6))
            self.screen.blit(self.font.render(f"Steps: {self.steps}", True, WHITE), (8, 32))

        pygame.display.flip()
        if fps is not None and fps > 0:
            self.clock.tick(fps)

    def close(self) -> None:
        if self.screen is not None:
            pygame.display.quit()
            self.screen = None
            self.clock = None

    # ---------------- 内部方法 ----------------

    def _ensure_display(self) -> None:
        """惰性创建窗口；headless 创建对象时不开窗。"""
        if self.screen is not None:
            return
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.display.get_init():
            pygame.display.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake RL")
        self.clock = pygame.time.Clock()

    def _spawn_food(self) -> None:
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                self.food = pos
                return

    def _get_state(self) -> np.ndarray:
        """10 维状态向量：文档 §5.2 状态空间。"""
        head_x, head_y = self.snake[0]
        food_dx = (self.food[0] - head_x) / GRID_WIDTH
        food_dy = (self.food[1] - head_y) / GRID_HEIGHT

        # 四周危险判定：以"下一步是否合法"为标准
        # 注意：尾巴下一步会移走，所以排除尾节点；如刚吃食物则整条蛇都在。
        tail = self.snake[-1] if not getattr(self, "_just_ate", False) else None
        body_set = set(self.snake)
        if tail is not None:
            body_set.discard(tail)

        danger_up = int(head_y == 0 or (head_x, head_y - 1) in body_set)
        danger_down = int(head_y == GRID_HEIGHT - 1 or (head_x, head_y + 1) in body_set)
        danger_left = int(head_x == 0 or (head_x - 1, head_y) in body_set)
        danger_right = int(head_x == GRID_WIDTH - 1 or (head_x + 1, head_y) in body_set)

        moving_up = int(self.direction == UP)
        moving_down = int(self.direction == DOWN)
        moving_left = int(self.direction == LEFT)
        moving_right = int(self.direction == RIGHT)

        return np.array([
            food_dx, food_dy,
            danger_up, danger_down, danger_left, danger_right,
            moving_up, moving_down, moving_left, moving_right,
        ], dtype=np.float32)