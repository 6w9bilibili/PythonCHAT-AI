#!/usr/bin/env python3
"""Train a GPT-like model from scratch using Hugging Face Trainer.

This is a minimal/example script for small experiments (tiny model by default).
It expects a tokenizer directory created by scripts/train_tokenizer.py and
training data in data/training.jsonl.

Note: From-scratch training requires much more data than a small chat log.
This script is intended for experimentation and pipeline completeness.
"""
import argparse
import os
from datasets import load_dataset
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
)


def build_dataset(data_jsonl: str, tokenizer, seq_len: int):
    ds = load_dataset('json', data_files=data_jsonl, split='train')

    def concat_examples(ex):
        text = ex.get('instruction', '')
        if ex.get('input'):
            text += '\n输入:\n' + ex.get('input', '')
        text += '\n回答:\n' + ex.get('output', '')
        return {'text': text}

    ds = ds.map(concat_examples, remove_columns=ds.column_names)

    def tokenize_fn(ex):
        return tokenizer(ex['text'], truncation=True, max_length=seq_len)

    tokenized = ds.map(tokenize_fn, batched=True, remove_columns=['text'])
    return tokenized


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/training.jsonl')
    parser.add_argument('--tokenizer_dir', default='tokenizer')
    parser.add_argument('--output', default='outputs/from_scratch')
    parser.add_argument('--model_size', choices=['tiny','small','medium'], default='tiny')
    parser.add_argument('--seq_len', type=int, default=512)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch', type=int, default=4)
    args = parser.parse_args()

    if not os.path.exists(args.tokenizer_dir):
        raise SystemExit('Tokenizer directory not found. Run scripts/train_tokenizer.py first')

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_dir, use_fast=True)
    # ensure pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    tokenized = build_dataset(args.data, tokenizer, args.seq_len)

    # model size mapping
    if args.model_size == 'tiny':
        n_layer = 6
        n_embd = 512
        n_head = 8
    elif args.model_size == 'small':
        n_layer = 12
        n_embd = 768
        n_head = 12
    else:
        n_layer = 24
        n_embd = 1024
        n_head = 16

    config = GPT2Config(
        vocab_size=len(tokenizer),
        n_positions=args.seq_len,
        n_ctx=args.seq_len,
        n_embd=n_embd,
        n_layer=n_layer,
        n_head=n_head,
    )

    model = GPT2LMHeadModel(config)

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=args.output,
        per_device_train_batch_size=args.batch,
        num_train_epochs=args.epochs,
        logging_steps=50,
        save_steps=500,
        save_total_limit=3,
        fp16=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(args.output)
    print('Training complete — model saved to', args.output)
    # write a simple metadata file indicating display name
    meta = {'display_name': 'PopSugerAI'}
    try:
        import json
        with open(os.path.join(args.output, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False)
        print('Wrote metadata with display_name PopSugerAI')
    except Exception:
        pass


if __name__ == '__main__':
    main()
