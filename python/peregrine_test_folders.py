#!/usr/bin/env python

import os
import re
import sys
import subprocess
import argparse

'''Script call sbatch scripts for testing in parallel'''

parser = argparse.ArgumentParser()
parser.add_argument('-c', required=True, type=str, help="Config-file for sbatch script")
parser.add_argument('-e', required=True, type=str, help="Experiment-folder")

args = parser.parse_args()


if __name__ == '__main__':
	checkpoint_dir = args.e + 'checkpoints/'
	output_dir =  args.e + 'output/'
	
	outputs = [x[0] for x in os.walk(output_dir)][1:]
	checkpoints = [x[0] for x in os.walk(checkpoint_dir)][1:]
	
	for c in checkpoints:
		output = False
		num_c = re.findall(r'\d\d\d[\d]+', c.replace('p266548','p-Rik'))[0]		#find number but skip p266548
		for o in outputs:
			num_o = re.findall(r'\d\d\d[\d]+', o.replace('p266548','p-Rik'))[0]
			if num_o == num_c:
				output = True	#output file already exists, 
				break
		if not output:			# no output folder exists, call testing script		
			script_call = 'sbatch -J {0} /home/p266548/Documents/amr_Rik/Seq2seq/src/scripts/test.sh {1} per {2}/'.format('ep-' + num_c,args.c, c)
			print script_call		
