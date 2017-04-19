#!/bin/bash
#SBATCH --time=01:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=2G

source $1	#$1 is the config file, all parameter values are there

#model file in $2
FILE=$2 

test_script="/home/p266548/Documents/amr_Rik/Seq2seq/src/python/test_OMT_dir.py"

if [ $2 = "per" ]; then						# we are on peregrine, load modules
    echo "Train on Peregrine..."
    module load cuDNN/5.0-CUDA-7.5.18
	module load foss/2016a
	echo "Loading modules complete"
else
	echo "Not training on Peregrine..."
fi	

   
if [ -f $FILE ]; then
   echo "Model file exists, do testing"
   python $test_script -o $output -f $src -tf $FILE -beam_size $beamsize -max_sent_length $max_sent_length -repl $replace_unk -n_best $n_best -test_ext $test_ext -tgt_ext $tgt_ext
else
   echo "Model file doesn't exist, aborting..."
fi

