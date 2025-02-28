#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=8:00:00
#SBATCH --job-name=process_gutenberg
#SBATCH --output=process_gutenberg_%A_%a.out

srun python -u process_data.py

echo "Done"