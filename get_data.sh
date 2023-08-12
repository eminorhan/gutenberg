#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=48:00:00
#SBATCH --job-name=get_gutenberg
#SBATCH --output=get_gutenberg_%A_%a.out

srun python -u get_data.py

done