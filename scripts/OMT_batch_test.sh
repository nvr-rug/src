#!/bin/bash
#SBATCH --time=02:30:00
#IGNORE THIS SBATCH --nodes=1
#IGNORE THIS SBATCH --ntasks=12
#SBATCH --mem=12G
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

#very ugly way of calling multiple SLURM scripts

th /home/p266548/Documents/amr_Rik/OpenNMT/translate.lua -src $1 -output $2 -model $3 -beam_size $4 -max_sent_length $5 $6 -gpuid 1 -fallback_to_cpu

