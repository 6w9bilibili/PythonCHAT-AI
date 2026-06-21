# PythonCHAT-AI

这是一个为 Termux（Android 终端）准备的简单聊天机器人示例仓库。

包含两个运行模式：
- openai：使用 OpenAI Chat Completions API（需要设置 OPENAI_API_KEY）。
- local：一个轻量的规则/数学/时间应答本地备选实现，不依赖大型模型。

Termux 快速开始（在 Termux 中执行）：

```bash
pkg update && pkg upgrade -y
pkg install python git -y
python -m pip install --upgrade pip
pip install -r requirements.txt
```

复制环境文件并填写 API Key（可选）：
```bash
cp .env.example .env
# 编辑 .env，填写 OPENAI_API_KEY
```

运行：
```bash
python3 chat.py --mode local    # 本地离线模式
python3 chat.py --mode openai   # 使用 OpenAI（需 API Key）
```

更多说明见下文文件。