#!/usr/bin/env python

import os
import re
import sys
import subprocess
import argparse

'''Script call sbatch scripts for testing in parallel'''

parser = argparse.ArgumentParser()
parser.add_argument('-f', required=True, type=str, help="Config-file for sbatch script")
parser.add_argument('-e', required=True, type=str, help="Experiment-folder")

args = parser.parse_args()


if __name__ == '__main__':
	if not os.path.isfile(args.f):
		raise ValueError("File doesn't exist")
	
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
		if not output:			# no output folder exists, call testing script with sbatch		
			subprocess.call(['sbatch', '-J', 'e' + num_c , '/home/p266548/Documents/amr_Rik/Seq2seq/src/scripts/test.sh', args.f, 'per', c + '/'])	
