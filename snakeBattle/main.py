#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py —— 入口：简易开局菜单 -> 进入对局

第一版菜单只做模式选择：
    按 1：人机对战（简单电脑）
    按 2：双人对战（WASD vs 方向键）
    按 ESC：退出
完整的开局菜单（席位配置、难度选择、结算排名）等第一版确认后再加。
"""

import pygame
import sys

from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GRAY, GREEN, YELLOW
from game import Game, MODE_PVP, MODE_AI, get_font


def draw_menu(screen: pygame.Surface, fonts: tuple) -> None:
    """画一帧菜单。"""
    font_title, font_item, font_tip = fonts
    screen.fill(BLACK)

    title = font_title.render("贪吃蛇对战", True, GREEN)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

    items = [
        ("按 1：人机对战（简单电脑）", YELLOW),
        ("按 2：双人对战（玩家1 WASD  vs  玩家2 方向键）", YELLOW),
        ("按 ESC：退出", GRAY),
    ]
    y = 290
    for text, color in items:
        surf = font_item.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, y)))
        y += 70

    tip = font_tip.render("对局中：R 重开    M 回菜单    ESC 回菜单", True, GRAY)
    screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))
    pygame.display.flip()


def choose_mode(screen: pygame.Surface, fonts: tuple) -> str | None:
    """菜单循环，返回模式名；ESC / 关窗返回 None。"""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    return MODE_AI
                if event.key in (pygame.K_2, pygame.K_KP2):
                    return MODE_PVP
                if event.key == pygame.K_ESCAPE:
                    return None
        draw_menu(screen, fonts)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("贪吃蛇对战")
    # 关闭文本输入：否则中文输入法（拼音等）会把字母键"吃"去组词，
    # 游戏收不到 KEYDOWN（典型症状：数字键正常、WASD/R/M 全没反应）
    pygame.key.stop_text_input()
    fonts = (get_font(56), get_font(32), get_font(20))

    while True:
        mode = choose_mode(screen, fonts)
        if mode is None:
            break
        result = Game(mode).run()  # run() 返回 "menu" 表示回菜单
        if result != "menu":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
