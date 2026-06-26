# Training and logging utilities for PopSugerAI

This module provides a small ConversationLogger that appends conversation turns to a JSONL file.
Each line is a JSON object with keys: user, assistant, timestamp.

Usage:
    from logger import ConversationLogger
    logger = ConversationLogger('data/conversations.jsonl')
    logger.log_turn('你好', '你好！有啥可以帮忙的？')

The logger ensures the parent directory exists and opens the file in append mode.

