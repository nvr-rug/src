#!/bin/bash

#evaluation script

source $1

if [ $2 = "bio" ]; then					
    echo "Testing with bio script..."
    evaluate_script=evaluate_bio.py
    python $python_path$evaluate_script -g $rawdata_test -mx $max_threads -train_size $train_size -roots_to_check $output_folder -exp_name $exp_name
else
	echo "Not testing with bio script"
	evaluate_script=evaluate.py
	python $python_path$evaluate_script -g $rawdata_test -mx $max_threads -train_size $train_size -roots_to_check $output_folder -exp_name $exp_name
fi	


