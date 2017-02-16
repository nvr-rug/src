#!/usr/bin/env python

import os
import re
import sys
import subprocess
import argparse
from multiprocessing import Pool

'''Script that produces the Smatch output for CAMR, Boxer and Seq2seq produced AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument('-g', required=True, type=str, help="Gold file")
parser.add_argument('-exp_name', required = True, type=str, help="Name of experiment")
parser.add_argument('-mx', required=False, type=int, default = 4, help="Number of maxthreads")
parser.add_argument('-rs', required=False, type=int, default = 4, help="Number of restarts for smatch")
parser.add_argument('-train_size', required=False, type=int, default = 33248 , help="Train size")
parser.add_argument('-range_sen', nargs='+', type=int, default = [], help ='Range of sentence length [min max]')
parser.add_argument('-range_words', nargs='+', type=int, default = [], help ='Set range of words instead of chars [min max]')
parser.add_argument('-roots_to_check', required = True, help = 'Root folder to check for output results')

args = parser.parse_args()


def do_smatch(os_call, range_check):
	'''Runs the smatch OS call'''
	
	output = subprocess.check_output(os_call, shell=True)
	f_score = output.split()[-1]		# get F-score from output
	num_sen = output.split()[-4]
	
	if range_check:
		skipped_sen = output.split()[-7]
		processed_sen = int(total_sen) - int(skipped_sen)
		print 'Skipped sentences for {0} : {1} out of {4} (range {2}-{3})'.format(f.split('-')[-1].replace('.txt',''), skipped_sen, args.range_words[0], args.range_words[1], total_sen)
		return f_score, processed_sen
	else:	
		return f_score, num_sen


def evaluate(gold_f, produced_f, epoch, res_dict, id_num):
	'''Will print smatch scores for Seq2seq checkpoints'''
	
	one_line = '--one_line'
	
	print_m = '{0} epochs {1}:'.format(epoch, id_num)
	num_tabs = '\t' * int(((8*4) - len(print_m)) / 8)
		
	if not args.range_sen and not args.range_words: # the normal output
		os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r {3} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.rs)
		f_score, num_sen = do_smatch(os_call, False)
		res_dict.append([epoch, '{0}{1} {2}'.format(print_m, num_tabs, f_score)])
	
	elif args.range_words and not args.range_sen:		#only calculate smatch for sentences with certain word range
		os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch_max_length.py -w1 {3} -w2 {4} -r {5} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.range_words[0], args.range_words[1], args.rs)	
		f_score, processed_sen = do_smatch(os_call, True)
		res_dict.append([epoch, '{0}{1} {2}'.format(print_m, num_tabs, f_score)])
		
	elif args.range_sen and not args.range_words:			# only calculate smatch score for sentences within a certain character range
		os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch_max_length.py -b1 {3} -b2 {4} -r {5} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.range_sen[0], args.range_sen[1], args.rs)	
		f_score, processed_sen = do_smatch(os_call, True)
		res_dict.append([epoch, '{0}{1} {2}'.format(print_m, num_tabs, f_score)])
		
	else:
		raise ValueError("Don't do both range_sen and range_words")
								
	return res_dict


if __name__ == '__main__':
	#ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.wiki.coref']
	#ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.wiki.coref','.seq.amr.restore.wiki.coref']
	ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.coref', '.seq.amr.restore.pruned', '.seq.amr.restore.pruned.wiki.coref.all']
	
	dirs_to_check = os.walk(args.roots_to_check).next()[1]
	
	print 'Results for {0}'.format(args.exp_name)
	
	res_dict = []
	
	for idx, root in enumerate(dirs_to_check):
		root_fix = args.roots_to_check + root
		for id_num in ids:
			for r,dirs,files in os.walk(root_fix):
				for f in files:
					if f.endswith(id_num):
						f_path = os.path.join(r,f)
						epoch = round(float(re.findall(r'\d\d\d[\d]+', f_path)[1]) / float(args.train_size),1)			#skip p266548 (hacky)
						res_dict = evaluate(args.g, f_path, epoch, res_dict, id_num)
	
	res_dict.sort(key=lambda x: x[0])
	for l in res_dict:
		print l[1]					
