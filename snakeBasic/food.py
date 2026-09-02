#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 17:18:06 2025

@author: ulyanov
"""

import pygame
import random
from config import *

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()
    
    def spawn(self, snake_positions=None):
        # 随机生成食物位置
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            # 确保食物不会出现在蛇身上
            if snake_positions is None or self.position not in snake_positions:
                break
    
    def draw(self, surface):
        pygame.draw.rect(surface, RED, 
                        (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, 
                         GRID_SIZE, GRID_SIZE))
    
    def check_eaten(self, head_position):
        """更可靠的食物吃掉检测"""
        return abs(self.position[0] - head_position[0]) < 0.5 and \
               abs(self.position[1] - head_position[1]) < 0.5