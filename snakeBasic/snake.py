#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 17:05:55 2025

@author: ulyanov
"""
# snake.py


import pygame
import numpy as np
from config import *

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # 蛇初始位置在屏幕中央
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        # 初始方向向右
        self.direction = RIGHT
        self.score = 0
        # 添加初始身体部分
        for i in range(1, self.length):
            self.positions.append(
                (self.positions[0][0] - i * self.direction[0], 
                 self.positions[0][1] - i * self.direction[1])
            )
    
    def get_head_position(self):
        return self.positions[0]
    
    def move(self, direction=None):
        if direction is not None:
            # 防止直接反向移动
            if (direction[0] * -1, direction[1] * -1) != self.direction:
                self.direction = direction
        
        head = self.get_head_position()
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # 检查是否撞墙
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False  # 游戏结束
        
        # 检查是否撞到自己
        if new_head in self.positions[1:]:
            return False  # 游戏结束
        
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        
        return True  # 游戏继续
    
    def grow(self):
        self.length += 1
        self.score += 10
    
    def get_state(self):
        """返回当前游戏状态，用于深度学习"""
        # 简化版状态表示
        head = self.get_head_position()
        return np.array([
            head[0] / GRID_WIDTH,  # 头部x坐标归一化
            head[1] / GRID_HEIGHT,  # 头部y坐标归一化
            self.direction[0],      # 方向x分量
            self.direction[1]       # 方向y分量
        ])
    
    def draw(self, surface):
        # 绘制蛇头
        head = self.positions[0]
        pygame.draw.rect(surface, GREEN, 
                        (head[0] * GRID_SIZE, head[1] * GRID_SIZE, 
                         GRID_SIZE, GRID_SIZE))
        
        # 绘制蛇身
        for position in self.positions[1:]:
            pygame.draw.rect(surface, BLUE, 
                            (position[0] * GRID_SIZE, position[1] * GRID_SIZE, 
                             GRID_SIZE, GRID_SIZE))