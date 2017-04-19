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

def write_list_to_file(lst, f):
	with open (f, 'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		

def write_to_file(sent, f):
	with open(f,'w') as out_f:
		out_f.write(sent.strip() + '\n')
	out_f.close()	

def do_smatch(amr1, amr2):
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r 10 --one_line -f {0} {1}'.format(amr1, amr2)
	
	output = subprocess.check_output(os_call, shell=True)
	f_score = output.split()[-1]
	
	return float(f_score)


def get_senlen(sent):
	words = 0
	spl_sen = sent.split()
	for s in spl_sen:
		if len(s) > 1:
			words += 1
		elif s.isdigit() or s.isalpha():
			words += 1
	
	return words		


def write_multiple_files(lst, root, prefix):
	camr = [x[0].strip() for x in lst] 
	seq = [x[1].strip() for x in lst]
	gold = [x[2].strip() for x in lst]
	sents = [x[3].strip() for x in lst]
	
	camr_file = root + prefix + '_camr.txt.ol'
	seq_file = 	root + prefix + '_seq.txt.ol'	
	gold_file = root + prefix + '_gold.txt.ol'
	sents_file = root + prefix +'_sents.sent'
	
	write_list_to_file(camr, camr_file)
	write_list_to_file(seq, seq_file)
	write_list_to_file(gold, gold_file)
	write_list_to_file(sents, sents_file)
	
	
if __name__ == '__main__':

	gold = [x.strip() for x in open(args.g, 'r') if x]
	f1 = [x.strip() for x in open(args.f1, 'r') if x]
	f2 = [x.strip() for x in open(args.f2, 'r') if x]
	sents = [x.strip() for x in open(args.s, 'r') if x]
	
	assert len(gold) == len(f1) == len(f2) == len(sents)
	
	res_list = []
	better = []
	worse = []
	
	best_amr = []
	
	for idx in range(len(gold)):
		if idx % 25 == 0 and idx != 0:
			print idx

		write_to_file(gold[idx], 'temp_gold.txt')
		write_to_file(f1[idx], 'temp_f1.txt')
		write_to_file(f2[idx], 'temp_f2.txt')
		
		senlen = get_senlen(sents[idx])
		fscore_1 = do_smatch('temp_f1.txt', 'temp_gold.txt')
		fscore_2 = do_smatch('temp_f2.txt', 'temp_gold.txt')
		
		if fscore_2 > fscore_1:
			better.append([f1[idx], f2[idx], gold[idx], sents[idx]])
			best_amr.append(f2[idx])
		elif fscore_2 < fscore_1:
			worse.append([f1[idx], f2[idx], gold[idx], sents[idx]])
			best_amr.append(f1[idx])
		else:
			best_amr.append(f2[idx])	
	
	write_list_to_file(best_amr, '/home/p266548/Documents/amr_Rik/sem_eval_testdata/extra_analysis/comparison_CAMR_seq/best_combination/best_combination_camr_seq.txt.ol')
	#write_multiple_files(better, '/home/p266548/Documents/amr_Rik/sem_eval_testdata/extra_analysis/comparison_CAMR_seq/seq2seq_better/', 'better')
	#write_multiple_files(worse, '/home/p266548/Documents/amr_Rik/sem_eval_testdata/extra_analysis/comparison_CAMR_seq/seq2seq_worse/', 'worse')
