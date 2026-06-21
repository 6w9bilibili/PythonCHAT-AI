"""
数据预处理脚本：把 data/conversations.jsonl 中的对话轮次转换为训练用的 JSONL（instruction tuning 风格）

输入格式（每行）：
{"user": "...", "assistant": "...", "timestamp": "..."}

输出格式：每行一个 JSON：
{"instruction": "用户: <user>", "input": "", "output": "<assistant>"}

用法：
    python3 data_prep.py --input data/conversations.jsonl --output data/training.jsonl

可以在本地或 Colab 上运行，在上传到 OpenAI 或 Hugging Face 训练前清洗和合并数据。
"""

import json
import argparse

def convert_turn_to_instruction(turn):
    user = turn.get('user', '').strip()
    assistant = turn.get('assistant', '').strip()
    if not user or not assistant:
        return None
    instruction = f"用户: {user}"
    return {"instruction": instruction, "input": "", "output": assistant}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/conversations.jsonl')
    parser.add_argument('--output', default='data/training.jsonl')
    args = parser.parse_args()

    seen = set()
    count_in = 0
    count_out = 0
    with open(args.input, 'r', encoding='utf-8') as fin, open(args.output, 'w', encoding='utf-8') as fout:
        for line in fin:
            count_in += 1
            try:
                obj = json.loads(line)
            except Exception:
                continue
            inst = convert_turn_to_instruction(obj)
            if not inst:
                continue
            # simple dedupe by instruction+output
            key = (inst['instruction'], inst['output'])
            if key in seen:
                continue
            seen.add(key)
            fout.write(json.dumps(inst, ensure_ascii=False) + '\n')
            count_out += 1

    print(f"Converted {count_in} turns -> {count_out} training examples to {args.output}")

if __name__ == '__main__':
    main()
