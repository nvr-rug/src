#!/bin/bash

#SBATCH --time=00:30:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=15G

source $1	#$1 is the config file, there is all the information about the parameters

train_script="/home/p266548/Documents/amr_Rik/OpenNMT/train.lua"

if [ $2 = "per" ]; then						# we are on peregrine, load modules
    echo "Train on Peregrine..."
    module load cuDNN/5.0-CUDA-7.5.18
	module load foss/2016a
	module load requests/2.7.0-goolfc-2.7.11-Python-2.7.9
	echo "Loading modules complete"
else
	echo "Not training on Peregrine..."
fi	

th $train_script -data $data_t7 -save_model $save_model -src_word_vec_size $src_word_vec_size -tgt_word_vec_size $tgt_word_vec_size -layers $layers -rnn_size $rnn_size -rnn_type $rnn_type -dropout $dropout $rnn_t -max_batch_size $batch_size -learning_rate $learning_rate -max_grad_norm $max_grad_norm -learning_rate_decay $learning_rate_decay -start_decay_at $start_decay_at -decay $decay -save_every $save_every -report_every $report_every -start_epoch $start_epoch -end_epoch $end_epoch -curriculum $curriculum $add_train_from -gpuid $gpuid $fall_back -log_file $log_file_train
