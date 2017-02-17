#!/bin/bash

#SBATCH --time=01:30:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=15G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rikvannoord@gmail.com

#Script that can also run on Peregrine

#source ../../config/config_test.sh
source $1

if [ $2 = "per" ]; then						# we are on peregrine, load modules
    echo "Train on Peregrine..."
    module load Python/2.7.11-foss-2016a
	module load tensorflow/0.9.0-foss-2016a-Python-2.7.11-CUDA-7.5.18
	echo "Loading modules complete"
else
	echo "Not training on Peregrine..."
fi	

mkdir -p $vocab_folder
mkdir -p $checkpoint_folder

translate=translate.py

python $python_path$translate --batch_size $batch_size --data_dir $vocab_folder --train_dir $checkpoint_folder --size=$node_size --num_layers=$num_layers --eps_per_checkpoint=$eps_per_checkpoint --save_folder_checkpoint $save_folder_checkpoint --en_vocab_size=$vocab_size --fr_vocab_size=$vocab_size --prod_ext $prod_ext --checkpoint_dest $checkpoint_dest --train_file $train_file --test_file $dev_file --input_ext $char_input_ext --output_ext $char_output_ext --min_vocab $min_vocab
