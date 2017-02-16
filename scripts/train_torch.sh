#!/bin/bash

#SBATCH --time=2-23:55:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=15G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rikvannoord@gmail.com

#Script that can also run on Peregrine

source $1

if [ $2 = "per" ]; then						# we are on peregrine, load modules
    echo "Train on Peregrine..."
    module load Python/2.7.11-foss-2016a
	echo "Loading modules complete"
else
	echo "Not training on Peregrine..."
fi

preprocess=preprocess-shards.py
#preprocess=preprocess.py

torch_train=train.lua
hdf_train=-train.hdf5
hdf_val=-val.hdf5.1.hdf5
model=model

preprocess_script=$torch_folder$preprocess 

#preprocess for torch

#python $preprocess_script --srcfile $train_file$input_ext --targetfile $train_file$output_ext --srcvalfile $dev_file$input_ext --targetvalfile $dev_file$output_ext --outputfile $model_torch$exp_name --maxwordlength $max_word_length --seqlength $seq_length --chars 1 --batchsize $batch_size --shardsize $shard_size

#train with torch

#echo "Start training now"

th $torch_folder$torch_train -data_file $model_torch$exp_name$hdf_train -val_data_file $model_torch$exp_name$hdf_val -savefile $model_torch$model -use_chars_enc 1 -use_chars_dec 1 -epochs 500 -attn 1 -brnn 1 -num_layers $num_layers -rnn_size $node_size -epochs $epochs -num_shards $num_shards

