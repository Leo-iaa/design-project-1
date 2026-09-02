#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_rl_snake.py —— 演示入口

文档 §7.2：轻量入口，加载已训练模型并可视化 AI 自动游戏。
"""

from snakeRL import play_with_model


if __name__ == "__main__":
    play_with_model(model_path="snake_model.pth", games=5, max_steps=500)