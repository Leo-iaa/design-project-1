#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent.py —— DQN / ReplayMemory / DQNAgent

依据：基于强化学习的贪吃蛇游戏 —— 软件详细设计文档 §5 强化学习核心设计。
"""

import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .config import (
    LEARNING_RATE, GAMMA, BATCH_SIZE, MEMORY_CAPACITY,
    EPSILON_START, EPSILON_END, EPSILON_DECAY, TARGET_UPDATE,
)


class DQN(nn.Module):
    """三层全连接 Q 网络（文档 §5.4）：输入 10 维 → 64 → 64 → 4。"""

    def __init__(self, input_size: int = 10, output_size: int = 4):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


class ReplayMemory:
    """经验回放缓冲区（文档 §5.5）：用 deque 实现 FIFO。"""

    def __init__(self, capacity: int = MEMORY_CAPACITY):
        self.memory: deque = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done) -> None:
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        return len(self.memory)


class DQNAgent:
    """DQN 智能体（文档 §5.6 / §6）：ε-贪婪 + 经验回放 + 双网络。"""

    def __init__(self, state_size: int = 10, action_size: int = 4):
        self.state_size = state_size
        self.action_size = action_size
        self.epsilon = EPSILON_START
        self.memory = ReplayMemory(MEMORY_CAPACITY)
        self.steps = 0

        self.policy_net = DQN(state_size, action_size)
        self.target_net = DQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=LEARNING_RATE)
        self.criterion = nn.MSELoss()

    # ---------- 决策 ----------
    def select_action(self, state: np.ndarray, greedy: bool = False) -> int:
        """选择动作；greedy=True 时跳过 ε-随机（用于演示）。"""
        if not greedy and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        with torch.no_grad():
            q = self.policy_net(torch.from_numpy(state).float().unsqueeze(0))
        return int(q.argmax(dim=1).item())

    # ---------- 学习 ----------
    def remember(self, state, action, reward, next_state, done) -> None:
        self.memory.push(state, action, reward, next_state, done)

    def replay(self, batch_size: int = BATCH_SIZE) -> float:
        if len(self.memory) < batch_size:
            return 0.0

        batch_data = self.memory.sample(batch_size)
        states, actions, rewards, next_states, dones = zip(*batch_data)

        states = torch.from_numpy(np.array(states, dtype=np.float32))
        actions = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        next_states = torch.from_numpy(np.array(next_states, dtype=np.float32))
        dones = torch.tensor(dones, dtype=torch.float32)

        current_q = self.policy_net(states).gather(1, actions).squeeze(1)

        with torch.no_grad():
            next_q = self.target_net(next_states).max(dim=1)[0]
            target_q = rewards + GAMMA * next_q * (1.0 - dones)

        loss = self.criterion(current_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=10.0)
        self.optimizer.step()

        self.steps += 1
        if self.steps % TARGET_UPDATE == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        return float(loss.item())

    def update_epsilon(self) -> None:
        self.epsilon = max(EPSILON_END, self.epsilon * EPSILON_DECAY)

    # ---------- 持久化 ----------
    def save(self, path: str) -> None:
        torch.save(self.policy_net.state_dict(), path)

    def load(self, path: str) -> None:
        sd = torch.load(path, map_location="cpu", weights_only=True)
        self.policy_net.load_state_dict(sd)
        self.target_net.load_state_dict(sd)