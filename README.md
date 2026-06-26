# PopSugerAI

PopSugerAI — a lightweight, Termux-friendly chatbot and training pipeline derived from the original PythonCHAT-AI project.

This repository now includes tools to collect conversation logs, prepare training data, train a tokenizer and train a GPT-like model from scratch (for experimentation).

Quick start

1) Install dependencies (adjust torch to your CUDA version):

    pip install -r requirements.txt

2) Collect conversations by running chat.py in local mode (it appends turns to data/conversations.jsonl):

    python3 chat.py --mode local

3) Prepare training JSONL (already provided by data_prep.py):

    python3 data_prep.py --input data/conversations.jsonl --output data/training.jsonl

4) Make corpus and train tokenizer:

    python3 scripts/make_corpus.py --input data/training.jsonl --output data/corpus.txt
    python3 scripts/train_tokenizer.py --corpus data/corpus.txt --out tokenizer

5) Train from scratch (tiny model recommended for single-GPU experimentation):

    python3 scripts/train_from_scratch.py --data data/training.jsonl --tokenizer_dir tokenizer --output outputs/from_scratch --model_size tiny --epochs 3 --batch 4

After training the model will save a metadata.json that contains "display_name": "PopSugerAI" which inference wrappers can read and display.
