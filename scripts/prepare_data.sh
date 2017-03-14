#!/bin/bash
# Prepare the data for a seq2seq model on character-level
# Presupposed that data is divided in training/dev/test sets

#source ../../config/config_test.sh
source $1

text_script=get_text_from_amrs.py
single_line_script=single_line_amr_directory.py

#choose char script here

char_script=prepare_all_char_level.py
#char_script=char_level_only_words.py

align_script=align_train_data.py

# for train, dev, test

#python $python_path$text_script -d $rawdata_train -out_folder $working_train -input_ext $input_ext -extension $amr_extension
#python $python_path$single_line_script -f $rawdata_train -tf $working_train -extension $amr_extension -output_ext $output_ext
python $python_path$char_script -f $working_train -output_ext $output_ext -input_ext $input_ext


#python $python_path$text_script -d $working_dev -out_folder $working_dev -input_ext $input_ext -extension $amr_extension
#python $python_path$single_line_script -f $working_dev -tf $working_dev -extension $amr_extension -output_ext $output_ext
python $python_path$char_script -f $working_dev -output_ext $output_ext -input_ext $input_ext 

#python $python_path$text_script -d $test_folder -out_folder $working_test -input_ext $input_ext -extension $amr_extension
#python $python_path$single_line_script -f $test_folder -tf $working_test -extension $amr_extension -output_ext $output_ext
python $python_path$char_script -f $working_test -output_ext $output_ext -input_ext $input_ext

python $python_path$align_script -a $working_train -s $working_train -o $train_file -char_input_ext $char_input_ext -char_output_ext $char_output_ext		#align train data to create "all" file
python $python_path$align_script -a $working_dev -s $working_dev -o $dev_file -char_input_ext $char_input_ext -char_output_ext $char_output_ext				#align dev data to create "all" file
