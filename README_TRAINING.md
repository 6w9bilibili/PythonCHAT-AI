Training guide and recommended workflow

This document explains how to collect data, prepare training JSONL, and run fine-tuning either
via OpenAI or with Hugging Face + PEFT (LoRA) on GPU/Colab.

1) Data collection (on Termux)
- Use the built-in logger: chat.py will now log turns to data/conversations.jsonl
- Each line is a JSON object {"user":"...","assistant":"...","timestamp":"..."}

2) Prepare training data
- Run:
    python3 data_prep.py --input data/conversations.jsonl --output data/training.jsonl
- This converts turns into instruction tuning format:
    {"instruction": "用户: <user>", "input": "", "output": "<assistant>"}

3) Fine-tuning options
- OpenAI fine-tune (Hosted):
  - Pros: managed, easy to start
  - Cons: cost, limited control
  - Steps: generate data/training.jsonl, then either use the OpenAI CLI or API to upload the file and start fine-tune. See openai_finetune.sh for an upload example.

- Hugging Face + PEFT (recommended for open-source models):
  - Pros: full control, can use LoRA/PEFT to reduce compute
  - Cons: requires GPU/Colab, more setup
  - Use train_peft.py as a starting template. Run on Colab or a machine with CUDA and sufficient VRAM.

4) Deploying model to Termux (inference)
- If using OpenAI: call the hosted model via API from chat.py (openai mode) or adapt to a wrapper.
- If using a local open-source model:
  - Fine-tune with PEFT/LoRA, merge weights, quantize if needed, and use on-device runtimes like llama.cpp or similar (depends on model format and compatibility).

5) Security and privacy
- 对话中可能包含敏感信息，请在上传训练前审查并清洗数据。

6) Next steps I can help implement
- 自动脱敏工具（删除邮箱/手机号等）
- 更复杂的 data_prep（合并多轮、构建上下文窗口）
- Colab-ready notebook for running train_peft.py
