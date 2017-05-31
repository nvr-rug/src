#!/bin/bash
#SBATCH --time=00:01:00
#IGNORE THIS SBATCH --nodes=1
#IGNORE THIS SBATCH --ntasks=12
#SBATCH --mem=12G
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

preprocess_script="/home/p266548/Documents/amr_Rik/OpenNMT/tools/release_model.lua"

th $preprocess_script -model $1 -gpuid 1

