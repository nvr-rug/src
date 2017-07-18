#!/bin/bash

#evaluation script for AMR parsing, $1 should be the configuration file

source $1

evaluate_script=OMT_evaluate.py

if [ $3 = "dev" ]; then
	echo "Evaluating dev results"
	python $python_path$evaluate_script -g $gold_files -roots_to_check $output_dev -exp_name $exp_name -eval_folder $eval_folder -type $2 -to_process $3
elif [ $3 = "test" ]; then
	echo "Evaluating test results"
	python $python_path$evaluate_script -g $gold_files -roots_to_check $output -exp_name $exp_name -eval_folder $eval_folder -type $2 -to_process $3
else
	echo "Last argument ($3) must be dev or test"
fi	


