#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=240GB
#SBATCH --time=4:00:00
#SBATCH --job-name=create_gutenberg_en
#SBATCH --output=create_gutenberg_en_%A_%a.out

export TRANSFORMERS_CACHE="/vast/eo41/huggingface"
export HF_DATASETS_CACHE="/vast/eo41/huggingface"

srun python -u create_dataset.py --wholedoc

echo "Done"