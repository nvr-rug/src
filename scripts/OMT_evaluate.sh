#!/bin/bash

#evaluation script for AMR parsing, $1 should be the configuration file

source $1

evaluate_script=evaluate.py
python $python_path$evaluate_script -g $gold_files -roots_to_check $output -exp_name $exp_name -eval_folder $eval_folder -check $2
	


