# 设计课题 1 —— 贪吃蛇三部曲

同一个贪吃蛇，三个阶段逐步进化：

| 模块 | 阶段 | 说明 |
|---|---|---|
| `snakeBasic/` | ① 经典版 | 单人贪吃蛇，经典五文件结构（OOP + Pygame） |
| `利用强化学习的贪吃蛇训练与运行代码/` | ② 强化学习版 | DQN 训练 AI 自动玩贪吃蛇 |
| `snakeBattle/` | ③ 多人对战版（当前主体） | 本地同屏对战：人机 1v1 + 双人对战 |

配套设计文档：
- 贪吃蛇游戏 Python 项目设计文档.pdf
- 基于强化学习的贪吃蛇游戏_详细设计文档.pdf

## 目录结构

```
.
├── snakeBasic/                    # ① 经典版
│   ├── config.py
│   ├── main.py
│   ├── game.py
│   ├── snake.py
│   └── food.py
│
├── snakeBattle/                   # ③ 多人对战版（当前主体）
│   ├── config.py                  # 网格/窗口/颜色/比分等常量
│   ├── main.py                    # 入口：开局菜单（选模式）
│   ├── game.py                    # 对局核心：同步走子碰撞判定、比分条、结算
│   ├── snake.py                   # 蛇：移动、转向缓冲队列
│   ├── food.py                    # 食物管理（支持多食物）
│   ├── ai.py                      # 电脑玩家（简单难度 AI）
│   └── selftest.py                # 开发用自测（headless，16 项断言）
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
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install pygame torch matplotlib numpy
```

只玩 snakeBattle 的话装 pygame 就够了；snakeRL 才需要 torch。

## 快速开始

### 1. 多人对战（snakeBattle）—— 推荐演示

```bash
cd snakeBattle
python main.py
```

菜单选模式：

| 按键 | 模式 |
|------|------|
| 1    | 人机对战（玩家 vs 简单电脑） |
| 2    | 双人对战（玩家1 WASD vs 玩家2 方向键） |
| ESC  | 退出 |

对局中按键：

| 按键 | 功能 |
|------|------|
| WASD / 方向键 | 玩家1 / 玩家2 转向 |
| R    | 重新开局 |
| M / ESC | 回菜单 |

**规则**：40×30 格棋盘，双方对角出生；先吃满 10 个食物或对方死亡者获胜；
两条蛇同帧头对头、互相穿过都会同归于尽判平局；顶部比分条实时显示战况。

### 2. 强化学习演示与训练（snakeRL）

```bash
cd 利用强化学习的贪吃蛇训练与运行代码

# 演示已训练模型（默认 5 局）
python demo_rl_snake.py

# 重新训练（默认 2000 局，headless 最快）
python -m snakeRL.train --episodes 2000
```

演示操作：P 暂停/继续，R 下一局，N 跳过当前局，ESC 退出。

训练产物：`snake_model.pth`（最终权重）、`snake_model_best.pth`（最佳权重）、
`training_progress.png`（得分与损失曲线）、`max_score.txt`（历史最高分）。

### 3. 经典版（snakeBasic）

```bash
cd snakeBasic
python main.py
```

## 关键技术点

### snakeBattle（多人对战）

- **同步走子碰撞判定**：先算所有蛇的新头，再统一判死——撞墙、头对头同格、
  对穿（互换位置）、撞"本步后仍占住的格子"（不长大的蛇尾巴会腾空）；
  死亡优先于得分，同帧全死 = 平局
- **输入缓冲队列**（最多 2 步）：每帧只应用一个转向，防"一帧按两键原地掉头自杀"
- **简单 AI**：先排除危险格（所有蛇身 + 对方蛇头四邻格，防对撞），再贪心选
  离食物最近的安全方向
- 已处理中文输入法吞键问题（`pygame.key.stop_text_input()` + scancode 物理键码兜底）

### snakeRL（强化学习）

- **状态空间（10 维）**：食物相对位置 + 四周危险 + 当前方向 one-hot
- **动作空间**：0=上, 1=下, 2=左, 3=右
- **奖励塑形**：吃食物 +20，撞墙/自身 −20，靠近 +1，远离 −1，停滞 −0.1，超时 −10
- **网络结构**：10 → 64 → 64 → 4（全连接 + ReLU）
- **训练技巧**：ε-贪婪探索、双网络（policy_net + target_net）、经验回放（deque）、梯度裁剪

详见 `基于强化学习的贪吃蛇游戏_详细设计文档.pdf`。
