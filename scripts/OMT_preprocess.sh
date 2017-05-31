#!/bin/bash
#Prepocess for OpenNMT experiments

source $1	#$1 is the config file, there is all the information about the parameters

preprocess_script="/home/p266548/Documents/amr_Rik/OpenNMT/preprocess.lua"

if [[ -z "$tgt_vocab" ]]; then
	echo "Normal preprocessing"
	th $preprocess_script -save_data $save_data $src_vocab $tgt_vocab -train_src $train_src -train_tgt $train_tgt -valid_src $valid_src -valid_tgt $valid_tgt -src_words_min_frequency $src_words_min_frequency -tgt_words_min_frequency $tgt_words_min_frequency -src_seq_length $src_seq_length -tgt_seq_length $tgt_seq_length -sort $sort -shuffle $shuffle -log_file $log_file_pp
else
	echo "Preprocessing from known vocabulary"
	th $preprocess_script -save_data $save_data -src_vocab $src_vocab -tgt_vocab $tgt_vocab -train_src $train_src -train_tgt $train_tgt -valid_src $valid_src -valid_tgt $valid_tgt -src_seq_length $src_seq_length -tgt_seq_length $tgt_seq_length -sort $sort -shuffle $shuffle -log_file $log_file_pp
fi	
