#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 17:19:15 2025

@author: ulyanov
"""

import pygame
import sys
from config import *
from snake import Snake
from food import Food

class Game:
    def __init__(self):
        # Pygame初始化
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        # 游戏对象初始化
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.score = 0
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 键盘控制
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.move(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.move(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.move(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.move(RIGHT)
                elif event.key == pygame.K_r and self.game_over:
                    # 重新开始游戏
                    self.snake.reset()
                    self.food.spawn()
                    self.game_over = False
                    self.score = 0
    
    def update(self):
        """更新游戏状态"""
        if not self.game_over:
            # 蛇移动
            if not self.snake.move():
                self.game_over = True
            
            # 检查是否吃到食物
            head = self.snake.get_head_position()
            if head == self.food.position:
                self.snake.grow()
                self.score = self.snake.score
                self.food.spawn()
                
                # 确保食物不会生成在蛇身上
                while self.food.position in self.snake.positions:
                    self.food.spawn()
    
    def draw(self):
        """绘制游戏画面"""
        # 清屏
        self.screen.fill(BLACK)
        
        # 绘制网格背景
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
        
        # 绘制游戏对象
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # 显示分数
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 游戏结束显示
        if self.game_over:
            game_over_text = self.font.render("游戏结束! 按R键重新开始", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        # 更新屏幕
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)