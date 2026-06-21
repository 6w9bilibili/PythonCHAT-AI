"""聊天入口脚本（已集成对话记录）

用法：
  python3 chat.py --mode local
  python3 chat.py --mode openai

会把每一轮（user/assistant）记录到 data/conversations.jsonl，方便后续用于训练数据准备。
"""

import argparse
import os
import sys
import json
from dotenv import load_dotenv
import requests
from simple_bot import SimpleBot
from logger import ConversationLogger
from datetime import datetime


def openai_chat_loop(api_key, logger=None):
    print("OpenAI 模式：开始会话。输入 exit/quit/q 退出。")
    system_prompt = "你是一个乐于助人的中文聊天机器人。回答尽量简短、友好。"
    messages = [{"role": "system", "content": system_prompt}]
    while True:
        try:
            user = input("你: ")
        except (KeyboardInterrupt, EOFError):
            print("\n已退出。")
            break
        if user.strip().lower() in ("exit", "quit", "q"):
            print("退出")
            break
        messages.append({"role": "user", "content": user})
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.8,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            assistant = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("请求 OpenAI 失败：", e)
            assistant = "抱歉，调用 OpenAI 接口出错。"
        print("AI:", assistant)
        messages.append({"role": "assistant", "content": assistant})
        # log
        if logger:
            try:
                logger.log_turn(user, assistant)
            except Exception:
                pass


def local_chat_loop(logger=None):
    print("本地模式：开始会话（规则/数学/时间）。输入 exit/quit/q 退出。")
    bot = SimpleBot()
    while True:
        try:
            user = input("你: ")
        except (KeyboardInterrupt, EOFError):
            print("\n已退出。")
            break
        if user.strip().lower() in ("exit", "quit", "q"):
            print("退出")
            break
        resp = bot.get_response(user)
        print("AI:", resp)
        if logger:
            try:
                logger.log_turn(user, resp)
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="Termux 友好的 Python 聊天机器人示例（带记录）")
    parser.add_argument("--mode", choices=["openai", "local"], default="local", help="运行模式: openai 或 local")
    args = parser.parse_args()

    logger = ConversationLogger('data/conversations.jsonl')

    if args.mode == "openai":
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("未检测到 OPENAI_API_KEY，无法使用 openai 模式。请在 .env 或环境变量中设置。")
            sys.exit(1)
        openai_chat_loop(api_key, logger=logger)
    else:
        local_chat_loop(logger=logger)


if __name__ == '__main__':
    main()
