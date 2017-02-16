#!/bin/bash

# let op  /*/ : ./call_tests.sh "/home/p266548/Documents/amr_Rik/Seq2seq/Experiments/best_permutation/checkpoints/*/"

source=$1

dir=$2

for d in $dir ; do
    if [[ -d $d ]]; then
		./test.sh $source notper $d &
    fi
done    
