Training guide and recommended workflow for PopSugerAI

This document explains how to collect data, prepare training JSONL, and run fine-tuning or from-scratch training with Hugging Face.

1) Data collection (on Termux)
- Use the built-in logger: chat.py logs turns to data/conversations.jsonl
- Each line is a JSON object {"user":"...","assistant":"...","timestamp":"..."}

2) Prepare training data
- Run:
    python3 data_prep.py --input data/conversations.jsonl --output data/training.jsonl
- This converts turns into instruction tuning format used by the training scripts

3) From-scratch training (example pipeline)
- Make corpus for tokenizer:
    python3 scripts/make_corpus.py --input data/training.jsonl --output data/corpus.txt
- Train tokenizer:
    python3 scripts/train_tokenizer.py --corpus data/corpus.txt --out tokenizer
- Train model from scratch (tiny recommended for quick experiments):
    python3 scripts/train_from_scratch.py --data data/training.jsonl --tokenizer_dir tokenizer --output outputs/from_scratch --model_size tiny

Notes:
- From-scratch training requires a lot of data for good results. If your dataset is small, prefer fine-tuning a pre-trained model (see train_peft.py).
- After a successful training, the model output directory contains metadata.json with display_name=PopSugerAI. Inference wrappers (chat.py or other) can read and display this name.

4) Fine-tuning (PEFT/LoRA)
- See train_peft.py for an example of using Hugging Face + PEFT for efficient fine-tuning. This is recommended when compute is limited.

5) Security and privacy
- 对话中可能包含敏感信息，请在上传训练前审查并清洗数据。
