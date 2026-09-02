#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train.py —— DQN 训练主循环

依据：基于强化学习的贪吃蛇游戏 —— 软件详细设计文档 §6 训练流程设计。
"""

from __future__ import annotations

import os
import time
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # 训练环境通常无显示，强制 Agg 后端
import matplotlib.pyplot as plt
import numpy as np

from .agent import DQNAgent
from .config import BATCH_SIZE, FPS
from .environment import SnakeEnv


def train_agent(
    episodes: int = 2000,
    render_every: Optional[int] = None,
    save_path: str = "snake_model.pth",
    progress_path: str = "training_progress.png",
    max_score_log: str = "max_score.txt",
) -> DQNAgent:
    """
    训练 DQN 智能体。

    参数:
        episodes:      总局数
        render_every:  每多少局渲染一次画面（None = 不渲染，最快）
        save_path:     最终模型保存路径
        progress_path: 训练曲线图保存路径
        max_score_log: 历史最高分持久化文件
    """
    env = SnakeEnv(headless=True)
    agent = DQNAgent(state_size=env._get_state().shape[0], action_size=4)

    scores: list[int] = []
    avg_scores: list[float] = []
    losses: list[float] = []

    best_score = _load_max_score(max_score_log)
    best_model_path = save_path.replace(".pth", "_best.pth")
    print(f"开始训练  episodes={episodes}  best(baseline)={best_score}")

    start = time.time()
    for ep in range(1, episodes + 1):
        state = env.reset()
        ep_reward = 0.0
        ep_losses: list[float] = []
        done = False

        while not done:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            ep_reward += reward
            agent.remember(state, action, reward, next_state, done)
            loss = agent.replay(BATCH_SIZE)
            if loss > 0:
                ep_losses.append(loss)
            state = next_state

            if render_every is not None and ep % render_every == 0:
                env.render(fps=FPS)

        agent.update_epsilon()
        scores.append(env.score)
        avg_scores.append(float(np.mean(scores[-10:])))
        losses.append(float(np.mean(ep_losses)) if ep_losses else 0.0)

        # 刷新最高分
        if env.score > best_score:
            best_score = env.score
            agent.save(best_model_path)
            _save_max_score(best_score, max_score_log)

        if ep % 10 == 0 or ep == 1:
            elapsed = time.time() - start
            print(
                f"Ep {ep:>4}/{episodes} | score={env.score:<3} "
                f"best={best_score:<3} avg10={avg_scores[-1]:.2f} "
                f"eps={agent.epsilon:.3f} loss={losses[-1]:.4f} "
                f"steps={env.steps} t={elapsed//60:.0f}m{elapsed%60:.0f}s"
            )

    # 保存 & 画曲线
    agent.save(save_path)
    print(f"训练完成。final={save_path}  best={best_model_path}({best_score})")
    _plot_curves(scores, avg_scores, losses, progress_path)
    return agent


# ---------- 小工具 ----------

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


def _plot_curves(scores, avg_scores, losses, out_path: str) -> None:
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(scores, label="score")
    plt.plot(avg_scores, "r-", linewidth=2, label="avg(10)")
    plt.xlabel("episode")
    plt.ylabel("score")
    plt.title("Training Score")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(losses, "g-", label="loss")
    plt.xlabel("episode")
    plt.ylabel("loss")
    plt.title("Training Loss")
    plt.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()


# ---------- CLI 入口 ----------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--render-every", type=int, default=None,
                        help="每 N 局渲染一次，调试时用；默认不渲染（训练更快）")
    parser.add_argument("--save", default="snake_model.pth")
    parser.add_argument("--plot", default="training_progress.png")
    args = parser.parse_args()

    train_agent(
        episodes=args.episodes,
        render_every=args.render_every,
        save_path=args.save,
        progress_path=args.plot,
    )