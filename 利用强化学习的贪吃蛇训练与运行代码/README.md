# 基于强化学习的贪吃蛇（DQN）

> 配套文档：`基于强化学习的贪吃蛇游戏_详细设计文档.pdf`

## 目录结构

```
利用强化学习的贪吃蛇训练与运行代码/
├── snake_model.pth         # 已训练好的模型权重
├── enhancedSnake.py        # 兼容入口：训练 + 演示
├── demo_rl_snake.py        # 轻量演示入口（仅加载模型演示）
└── snakeRL/                # 推荐拆分结构（文档 §2.2）
    ├── config.py           # 屏幕/网格/颜色/方向/DQN 超参数
    ├── environment.py      # SnakeEnv 游戏环境（reset/step/render）
    ├── agent.py            # DQN / ReplayMemory / DQNAgent
    ├── train.py            # train_agent() 训练主循环 + 训练曲线
    ├── demo_rl_snake.py    # 加载模型演示（含暂停/最高分/难度递增）
    └── __init__.py
```

## 运行

```bash
# 演示已训练模型（推荐先跑这条）
python demo_rl_snake.py

# 自定义演示参数
python -m snakeRL.demo_rl_snake --games 3 --max-steps 800

# 重新训练（耗时；约 2000 局）
python -m snakeRL.train --episodes 2000
```

## 演示模式操作

| 按键 | 功能       |
|------|-----------|
| P    | 暂停 / 继续 |
| R    | 下一局     |
| N    | 跳过当前局 |
| ESC  | 退出       |

## 改进点（相对原 enhancedSnake.py）

1. **结构**：单文件 → 拆 5 个职责清晰的小模块（与文档 §2.2 推荐结构一致）。
3. **环境接口**：SnakeEnv 支持 headless（训练更快），render() 惰性创建窗口。
4. **碰撞判定**：去掉原 `_just_ate` 错误逻辑；尾巴在不吃食物时下一步会移走，不应算"自身"碰撞。
5. **演示交互**：新增 P 暂停、R 重开、ESC 退出。
6. **难度递增**：随分数提升 FPS（每吃 2 个食物 +2 FPS，上限 60）。
7. **最高分持久化**：训练（best_model）和演示（demo）都会把最高分写入 `max_score.txt`。
8. **依赖清理**：删除 `IPython.display` / `matplotlib.animation` 等无谓导入；matplotlib 强制 Agg 后端，headless 训练不报错。
9. **梯度裁剪**：DQN 训练加入 `clip_grad_norm_(10.0)`，提高稳定性。