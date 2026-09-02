#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snakeRL 包初始化

对外暴露高层入口：
    train_agent(...)        训练
    play_with_model(...)     加载模型演示
"""

from .train import train_agent
from .demo_rl_snake import play_with_model

__all__ = ["train_agent", "play_with_model"]