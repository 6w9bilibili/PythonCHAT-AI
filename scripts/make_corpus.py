#!/usr/bin/env python3
"""Make corpus.txt from data/training.jsonl

Each line in data/training.jsonl is expected to be a JSON object with keys
`instruction`, `input`, `output`. This script concatenates them into a
single text line per example and writes data/corpus.txt which is suitable
for tokenizer training.
"""
import argparse
import json
from pathlib import Path


def make_corpus(input_path: str, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    count_in = 0
    count_out = 0
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            count_in += 1
            try:
                obj = json.loads(line)
            except Exception:
                continue
            parts = []
            inst = obj.get('instruction', '').strip()
            inp = obj.get('input', '').strip() if obj.get('input') else ''
            out = obj.get('output', '').strip()
            if inst:
                parts.append(inst)
            if inp:
                parts.append('输入: ' + inp)
            if out:
                parts.append('回答: ' + out)
            text = '\n'.join(parts).strip()
            if not text:
                continue
            fout.write(text.replace('\n', ' ') + '\n')
            count_out += 1
    print(f"Wrote {count_out} lines (from {count_in} input turns) to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/training.jsonl')
    parser.add_argument('--output', default='data/corpus.txt')
    args = parser.parse_args()
    make_corpus(args.input, args.output)
