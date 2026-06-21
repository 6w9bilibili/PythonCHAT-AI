"""
简单规则与数学处理的本地聊天机器人（轻量）

功能：
- 识别问候
- 返回当前时间/日期
- 简单数学计算（安全解析表达式）
- 若无匹配，返回随机短语

该模块无外部重度依赖，适合在 Termux 离线或无 API Key 场景下使用。
"""

import re
import datetime
import random
import ast
import operator as op


class SimpleBot:
    def __init__(self):
        self.greetings = ['你好', '您好', '嗨', 'Hello', 'hey']
        self.fallbacks = [
            '嗯，我明白了。你能详细说说吗？',
            '有意思，你有更多信息吗？',
            '我还在学习中，能换个问题吗？',
        ]

    def get_response(self, text: str) -> str:
        t = text.strip()
        if not t:
            return '你可以跟我说点什么。'
        low = t.lower()

        # greetings
        for g in self.greetings:
            if g.lower() in low:
                return random.choice(['你好！', '嗨，有什么可以帮你的？', '你好呀～'])

        # time/date
        if any(k in low for k in ['时间', '现在几点', '几点了', 'time']):
            return datetime.datetime.now().strftime('现在是 %Y-%m-%d %H:%M:%S')
        if any(k in low for k in ['日期', '今天几号', '几号']):
            return datetime.datetime.now().strftime('今天是 %Y-%m-%d')

        # math calculation: detect simple expressions or keywords
        if '计算' in low or re.search(r'[0-9]+\s*[-+*/%\\^]', low) or any(k in low for k in ['+', '-', '*', '/', '^']):
            expr = self._extract_expr(low)
            if expr:
                try:
                    val = self._safe_eval(expr)
                    return f'结果: {val}'
                except Exception as e:
                    return f'无法计算表达式：{e}'

        # help
        if any(k in low for k in ['帮助', '帮助我', '用法']):
            return '我可以回答问候、返回当前时间/日期、进行简单计算。要退出请输入 exit/quit/q。'

        # fallback
        return random.choice(self.fallbacks)

    def _extract_expr(self, text: str) -> str:
        # 提取数字与运算符的子串
        m = re.search(r'([0-9\(\)\.\s\+\-\*/%\\^]+)', text)
        if m:
            expr = m.group(1)
            expr = expr.replace('^', '**')
            return expr
        return ''

    def _safe_eval(self, expr: str):
        """使用 ast 解析并只允许安全表达式（数字和算术运算）"""
        # 支持的运算符映射
        allowed_operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.Mod: op.mod,
            ast.USub: op.neg,
            ast.UAdd: op.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Num):  # < Py3.8
                return node.n
            if isinstance(node, ast.Constant):  # Py3.8+
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError('不支持的常量')
            if isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                op_type = type(node.op)
                if op_type in allowed_operators:
                    return allowed_operators[op_type](left, right)
                raise ValueError('不支持的二元运算')
            if isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                op_type = type(node.op)
                if op_type in allowed_operators:
                    return allowed_operators[op_type](operand)
                raise ValueError('不支持的一元运算')
            raise ValueError('不支持的表达式')

        node = ast.parse(expr, mode='eval')
        return _eval(node)
