#!/usr/bin/env python3
"""Train a Byte-Level BPE tokenizer on corpus.txt and save to --out dir.

Usage:
  python scripts/train_tokenizer.py --corpus data/corpus.txt --out tokenizer
"""
import argparse
from pathlib import Path
from tokenizers import ByteLevelBPETokenizer


def train_tokenizer(corpus_path: str, out_dir: str, vocab_size: int = 32000, min_frequency: int = 2):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    tokenizer = ByteLevelBPETokenizer()
    tokenizer.train(files=[corpus_path], vocab_size=vocab_size, min_frequency=min_frequency,
                    special_tokens=["<s>", "<pad>", "</s>", "<unk>", "<mask>"])
    tokenizer.save_model(out_dir)
    print(f"Tokenizer saved to {out_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', default='data/corpus.txt')
    parser.add_argument('--out', default='tokenizer')
    parser.add_argument('--vocab_size', type=int, default=32000)
    parser.add_argument('--min_frequency', type=int, default=2)
    args = parser.parse_args()
    train_tokenizer(args.corpus, args.out, args.vocab_size, args.min_frequency)
