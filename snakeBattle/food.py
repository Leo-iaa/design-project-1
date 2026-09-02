#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
food.py —— 食物管理（支持场上同时有多个食物）

第一版 1v1 只放 1 个食物（config.FOOD_COUNT_1V1 = 1）；
以后做普通难度的"多食物抢吃"，把配置调大即可，逻辑不用改。
"""

import random

import pygame

from config import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, FOOD_COUNT_1V1, RED


class FoodManager:
    """管理场上所有食物的位置。"""

    def __init__(self, count: int = FOOD_COUNT_1V1) -> None:
        self.count = count
        self.positions: list[tuple[int, int]] = []

    def respawn_all(self, occupied: set[tuple[int, int]]) -> None:
        """开新局时：清空食物，重新铺满 count 个（绝不刷在蛇身上）。"""
        self.positions = []
        while len(self.positions) < self.count:
            self._spawn_one(occupied | set(self.positions))

    def remove(self, pos: tuple[int, int], occupied: set[tuple[int, int]]) -> None:
        """吃掉 pos 处的食物，并补一个新的（避开所有被占的格子）。"""
        if pos in self.positions:
            self.positions.remove(pos)
        self._spawn_one(occupied | set(self.positions))

    def _spawn_one(self, occupied: set[tuple[int, int]]) -> None:
        """在没被占的格子里随机放一个食物；棋盘几乎满了就放弃（极端情况）。"""
        free = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if free:
            self.positions.append(random.choice(free))

    def draw(self, surface: pygame.Surface, y_offset: int = 0) -> None:
        for pos in self.positions:
            pygame.draw.rect(
                surface, RED,
                (pos[0] * GRID_SIZE, y_offset + pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )
