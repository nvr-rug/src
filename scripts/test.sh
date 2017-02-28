#!/bin/bash
#SBATCH --time=01:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=2G

#source ../../config/config_test.sh
source $1

if [ $2 = "per" ]; then						# we are on peregrine, load modules
    echo "Test on Peregrine..."
    module load requests/2.7.0-goolfc-2.7.11-Python-2.7.9
	module load Python/2.7.11-foss-2016a
	module load tensorflow/0.9.0-foss-2016a-Python-2.7.11
	echo "Loading modules complete"
else
	echo "Not testing on Peregrine..."
fi	

test_seq2seq=test_seq2seq_dir.py

echo $3

python $python_path$test_seq2seq -max_threads $max_threads -f $test_folder -df $vocab_folder -tf $3 -sf $output_folder -size $node_size -layers $num_layers -python_path $python_path -input_ext $char_input_ext -output_ext $char_output_ext -en_vocab_size=$vocab_size -fr_vocab_size=$vocab_size
