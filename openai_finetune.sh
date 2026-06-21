#!/usr/bin/env bash
# 示例：使用 OpenAI CLI 上传并创建 fine-tune（需安装 openai CLI 并配置好 OPENAI_API_KEY）
# 注意：OpenAI 的 fine-tune 接口和可用模型会随时间变更，请参考官方文档。

if [ -z "$OPENAI_API_KEY" ]; then
  echo "请先设置环境变量 OPENAI_API_KEY"
  exit 1
fi

if [ ! -f data/training.jsonl ]; then
  echo "请先生成 data/training.jsonl（例如运行 python3 data_prep.py）"
  exit 1
fi

# 上传文件
openai api files.create -f data/training.jsonl -p "fine-tune"

# 假设返回了 file-id，使用下面命令创建 fine-tune（示例，实际参数按需调整）
# openai api fine_tunes.create -t <FILE_ID> -m gpt-3.5-turbo

echo "上传完成。请根据 openai CLI 输出的 file id 创建 fine-tune 任务。"
