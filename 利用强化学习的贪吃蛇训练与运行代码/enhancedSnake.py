#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhancedSnake.py —— 兼容入口

文档 2.2 节建议将代码拆分到 snakeRL/ 子包（config / environment / agent /
train / demo_rl_snake），本文件保留为统一调用入口，向下转发到子包。

运行方式（任选其一）:
    python enhancedSnake.py                # 训练 + 演示
    python demo_rl_snake.py                # 仅演示（加载已有模型）
"""

from snakeRL import train_agent, play_with_model


if __name__ == "__main__":
    # 1) 训练（如需重新训练，取消下一行注释；默认 ~2k 局耗时较长）
    # train_agent(episodes=2000, render_every=None)

    # 2) 演示已训练模型
    play_with_model(model_path="snake_model.pth", games=5, max_steps=500)