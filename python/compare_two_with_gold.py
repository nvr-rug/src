#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script that does individual comparison with 2 AMR files and a gold file
   AMRs should be in one-line format'''

import re,sys, argparse, os, subprocess, json
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-g", required = True, type=str, help="File with gold AMRs")
parser.add_argument("-f1", required = True, type=str, help="First file with AMRs")
parser.add_argument("-f2", required = True, type=str, help="Second file with AMRs")
parser.add_argument("-s", required = True, type=str, help="Gold sentences")

args = parser.parse_args()


def write_to_file(sent, f):
	with open(f,'w') as out_f:
		out_f.write(sent.strip() + '\n')
	out_f.close()	

def do_smatch(amr1, amr2):
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r 4 --one_line -f {0} {1}'.format(amr1, amr2)
	
	output = subprocess.check_output(os_call, shell=True)
	f_score = output.split()[-1]
	
	return float(f_score)

if __name__ == '__main__':

	gold = [x.strip() for x in open(args.g, 'r') if x]
	f1 = [x.strip() for x in open(args.f1, 'r') if x]
	f2 = [x.strip() for x in open(args.f2, 'r') if x]
	sents = [x.strip() for x in open(args.s, 'r') if x]
	
	assert len(gold) == len(f1) == len(f2) == len(sents)
	
	res_list = []
	better = 0
	for idx in range(len(gold)):
		if idx % 50 == 0 and idx != 0:
			print idx
		write_to_file(gold[idx], 'temp_gold.txt')
		write_to_file(f1[idx], 'temp_f1.txt')
		write_to_file(f2[idx], 'temp_f2.txt')
		
		fscore_1 = do_smatch('temp_f1.txt', 'temp_gold.txt')
		fscore_2 = do_smatch('temp_f2.txt', 'temp_gold.txt')
		
		if fscore_2 == fscore_1:
			better += 1

	print 'Equal AMRs = {0}'.format(better)	

