#!/bin/bash

#SBATCH --gres=gpu:a100:4
#SBATCH --cpus-per-task=16
#SBATCH --mem=480GB
#SBATCH --time=00:10:00
#SBATCH --job-name=train_gutenberg
#SBATCH --output=train_gutenberg_%A_%a.out
#SBATCH --array=0

export TRANSFORMERS_CACHE="/vast/eo41/huggingface"
export HF_DATASETS_CACHE="/vast/eo41/huggingface"

# root model directory
MODEL_ROOT_DIR="/vast/eo41/gutenberg/models"
SP="llama2-7B-gutenberg"

# gpt2-xl
accelerate launch --config_file accelerate_4gpu_config.yaml --num_cpu_threads_per_process 16 /vast/eo41/gutenberg/train.py \
    --model_name_or_path "meta-llama/Llama-2-7b" \
    --train_dir "data/text" \
    --val_dir "data/text_val" \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --learning_rate 0.00001 \
    --output_dir "${MODEL_ROOT_DIR}/${SP}" \
    --save_prefix ${SP} \
    --block_size 512 \
    --num_train_epochs 10 \
    --checkpointing_steps 1000 \
    --overwrite_cache

echo "Done"