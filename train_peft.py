"""
训练模板（PEFT/LoRA）示例（需在有 GPU 的环境或 Colab 上运行）

说明：
- 本脚本为模板，展示如何用 Hugging Face Transformers + PEFT 做 LoRA 微调。
- 在运行前需安装：transformers, datasets, accelerate, peft, evaluate
  pip install transformers datasets accelerate peft evaluate

注意：不同模型和 tokenizer 可能需要调整（tokenizer.pad_token 等）。
这个脚本假定训练文件是 data/training.jsonl，且每行是 JSON with keys instruction,input,output
"""

import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

MODEL_NAME = os.getenv('BASE_MODEL', 'gpt2')  # 请在运行时替换为合适的 base model，如 'decapoda-research/llama-7b-hf'

def preprocess(examples, tokenizer):
    texts = []
    for inst, inp, out in zip(examples['instruction'], examples['input'], examples['output']):
        # 简单拼接：instruction + input -> output
        if inp:
            prompt = f"{inst}\n输入:\n{inp}\n回答:\n"
        else:
            prompt = f"{inst}\n回答:\n"
        target = out
        texts.append((prompt, target))
    input_ids = [tokenizer(p, truncation=True, max_length=512)['input_ids'] for p, t in texts]
    labels = [tokenizer(t, truncation=True, max_length=256)['input_ids'] for p, t in texts]
    # 合并并返回 (这是一个非常简化的示例，应在实际项目中更仔细地处理拼接和 label 对齐)
    model_inputs = {'input_ids': input_ids, 'labels': labels}
    return model_inputs


def main():
    # 加载数据
    ds = load_dataset('json', data_files='data/training.jsonl', split='train')
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, return_dict=True)

    # PEFT/LoRA 配置（示例参数）
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=['q_proj', 'v_proj'] if 'llama' in MODEL_NAME else None,
        lora_dropout=0.05,
        bias='none',
        task_type='CAUSAL_LM'
    )

    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)

    # 简化：直接 tokenization 可能需要自定义 map
    def tok_fn(ex):
        return preprocess(ex, tokenizer)

    tokenized = ds.map(lambda ex: tokenizer(ex['instruction'] + '\n' + ex.get('input', ''), truncation=True, max_length=768), batched=True)

    training_args = TrainingArguments(
        output_dir='outputs',
        per_device_train_batch_size=2,
        num_train_epochs=1,
        logging_steps=10,
        save_strategy='epoch',
        fp16=True,
        remove_unused_columns=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained('outputs/peft_model')

if __name__ == '__main__':
    main()
