# Snake RL (DQN) —— 设计课题 1

基于强化学习（Deep Q-Network）的贪吃蛇游戏。  
配套设计文档：
- 贪吃蛇游戏 Python 项目设计文档.pdf
- 基于强化学习的贪吃蛇游戏_详细设计文档.pdf

## 目录结构

```
.
├── snakeBasic/                    # 阶段 A：经典五文件结构（OOP + Pygame）
│   ├── config.py
│   ├── main.py
│   ├── game.py
│   ├── snake.py
│   └── food.py
│
└── 利用强化学习的贪吃蛇训练与运行代码/
    ├── demo_rl_snake.py           # 演示入口：加载模型并可视化 AI 自动游戏
    ├── enhancedSnake.py           # 兼容入口（训练 + 演示）
    ├── README.md
    │
    └── snakeRL/                   # 推荐结构（文档 §2.2）
        ├── config.py              # 屏幕/网格/颜色/方向/DQN 超参数
        ├── environment.py         # SnakeEnv 游戏环境 (reset/step/render)
        ├── agent.py               # DQN / ReplayMemory / DQNAgent
        ├── train.py               # train_agent() 训练主循环 + 曲线
        ├── demo_rl_snake.py       # 演示（含暂停/最高分/难度递增）
        └── __init__.py
```

## 环境准备

```bash
# 推荐使用 venv
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install pygame torch matplotlib numpy
```

## 快速开始

### 1. 演示已训练模型

```bash
# 默认加载 snakeRL/../snake_model.pth，演示 5 局
python demo_rl_snake.py

# 自定义参数
python -m snakeRL.demo_rl_snake --games 3 --max-steps 800
```

演示操作：

| 按键 | 功能       |
|------|-----------|
| P    | 暂停 / 继续 |
| R    | 下一局     |
| N    | 跳过当前局 |
| ESC  | 退出       |

### 2. 重新训练 DQN 智能体

```bash
# 默认 2000 局、headless 不渲染（最快）
python -m snakeRL.train --episodes 2000

# 调试用，每 50 局渲染一次
python -m snakeRL.train --episodes 200 --render-every 50
```

训练产物：
- `snake_model.pth` —— 最终权重
- `snake_model_best.pth` —— 训练过程中最高分对应的权重
- `training_progress.png` —— 得分与损失曲线
- `max_score.txt` —— 历史最高分

## 关键技术点

- **状态空间（10 维）**：食物相对位置 + 四周危险 + 当前方向 one-hot
- **动作空间**：0=上, 1=下, 2=左, 3=右
- **奖励塑形**：吃食物 +20，撞墙/自身 −20，靠近 +1，远离 −1，停滞 −0.1，超时 −10
- **网络结构**：10 → 64 → 64 → 4（全连接 + ReLU）
- **训练技巧**：ε-贪婪探索、双网络（policy_net + target_net）、经验回放（deque）、梯度裁剪

详见 `基于强化学习的贪吃蛇游戏_详细设计文档.pdf`。