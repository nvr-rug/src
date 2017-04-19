#!/bin/bash
#SBATCH --time=01:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=2G

source $1	#$1 is the config file, all parameter values are there

#model file in $3
FILE=$3 

test_script="/home/p266548/Documents/amr_Rik/Seq2seq/src/python/test_OMT_dir.py"

if [ $2 = "per" ]; then						# we are on peregrine, load modules
    echo "Testing on Peregrine..."
    module load requests/2.7.0-goolfc-2.7.11-Python-2.7.9
    module load cuDNN/5.0-CUDA-7.5.18
	module load foss/2016a
	echo "Loading modules complete"
	. /home/p266548/torch/install/bin/torch-activate
else
	echo "Not training on Peregrine, but on GPU"
	gpu="-gpu gpu"
fi	

   
if [ -f $FILE ]; then
   echo "Model file exists, do testing"
   python $test_script -o $output -f $src -tf $FILE -beam_size $beamsize -max_sent_length $max_sent_length -repl $replace_unk -n_best $n_best -test_ext $test_ext -tgt_ext $tgt_ext $gpu
else
   echo "Model file doesn't exist, aborting..."
fi

