#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_rl_snake.py —— 加载已训练模型，用 pygame 实时演示 AI 自动游戏。

特性：
  · P 键暂停 / 继续
  · ESC 退出
  · 随分数自动提速（难度递增，FPS 上限 60）
  · 记录历史最高分到 max_score.txt
"""

from __future__ import annotations

import os
import sys
import time
from typing import Optional

import pygame

from .agent import DQNAgent
from .config import FPS
from .environment import SnakeEnv


def play_with_model(
    model_path: str = "snake_model.pth",
    games: int = 5,
    max_steps: int = 1000,
    max_score_log: str = "max_score.txt",
    start_fps: int = FPS,
    max_fps: int = 60,
) -> None:
    """加载模型并演示 AI 自动游戏。

    参数:
        model_path:    模型权重路径
        games:         演示局数
        max_steps:     单局最大步数（防止意外无限循环）
        max_score_log: 历史最高分文件
        start_fps:     起始 FPS
        max_fps:       FPS 上限（难度递增顶值）
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型不存在: {model_path}")

    # 字体可在窗口创建后再取
    env = SnakeEnv(headless=False)
    font = pygame.font.SysFont(None, 28)
    env.font = font
    env.reset()

    agent = DQNAgent(state_size=env._get_state().shape[0], action_size=4)
    agent.load(model_path)
    agent.epsilon = 0.0  # 演示纯利用

    best_ever = _load_max_score(max_score_log)
    print(f"加载模型 {model_path}  历史最高分={best_ever}")

    paused = False
    for game_idx in range(1, games + 1):
        state = env.reset()
        steps = 0
        done = False

        while not done and steps < max_steps:
            # -------- 输入 --------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        env.close()
                        return
                    if event.key == pygame.K_p:
                        paused = not paused
                    if event.key == pygame.K_r and done:
                        # 当前局已结束，按 R 重开下一局
                        break
            if paused:
                env.render(fps=30, show_info=True)
                _draw_pause_hint(env.screen, font)
                pygame.display.flip()
                env.clock.tick(15)
                continue

            # -------- 决策 --------
            action = agent.select_action(state, greedy=True)
            state, _, done = env.step(action)
            steps += 1

            # 难度递增：每吃 2 个食物，FPS +2，上限 max_fps
            current_fps = min(max_fps, start_fps + env.score * 2)
            env.render(fps=current_fps, show_info=True)

            # 顶部叠加最高分
            _draw_overlay(env.screen, font, env.score, best_ever, current_fps, paused)

        # 本局结束，停留片刻显示 GAME OVER
        best_ever = max(best_ever, env.score)
        _save_max_score(best_ever, max_score_log)

        _draw_game_over(env.screen, font, env.score, game_idx, games)
        pygame.display.flip()

        # 等玩家按 R 重开 / N 跳过 / ESC 退出；连续 3 秒无输入则自动进入下一局
        wait_for_next = True
        idle_start = time.time()
        while wait_for_next and done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        env.close()
                        return
                    if event.key == pygame.K_r:
                        wait_for_next = False
                    if event.key == pygame.K_n:
                        # 跳过当前局
                        wait_for_next = False
                        done = False
            env.clock.tick(15)
            if time.time() - idle_start > 3.0:
                wait_for_next = False  # 自动进入下一局

        print(f"Game {game_idx}/{games}: score={env.score}, steps={steps}")

    env.close()
    print(f"演示完成。最高分={best_ever}（已写入 {max_score_log}）")


# ---------- UI 辅助 ----------

def _draw_pause_hint(screen, font) -> None:
    text = font.render("PAUSED  (press P to resume)", True, (255, 255, 0))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, rect)


def _draw_overlay(screen, font, score: int, best: int, fps: int, paused: bool) -> None:
    info = font.render(f"Best: {best}  FPS: {fps}  {'[PAUSED]' if paused else ''}",
                         True, (200, 200, 200))
    screen.blit(info, (8, 56))


def _draw_game_over(screen, font, score: int, idx: int, total: int) -> None:
    msg1 = font.render(f"Game {idx}/{total}  Score: {score}", True, (255, 255, 255))
    msg2 = font.render("Press R for next, ESC to quit", True, (200, 200, 200))
    screen.blit(msg1, (8, 86))
    screen.blit(msg2, (8, 114))


def _load_max_score(path: str) -> int:
    if os.path.exists(path):
        try:
            return int(open(path, "r", encoding="utf-8").read().strip() or 0)
        except Exception:
            return 0
    return 0


def _save_max_score(score: int, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(score))


# ---------- CLI 入口 ----------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="snake_model.pth")
    parser.add_argument("--games", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=1000)
    args = parser.parse_args()

    play_with_model(
        model_path=args.model,
        games=args.games,
        max_steps=args.max_steps,
    )