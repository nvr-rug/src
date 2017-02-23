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


def filter_sent(sent_spl):
	sent = []
	for s in sent_spl:
		if len(s) == 1:
			if s.isdigit() or s.isalpha():
				sent.append(s)
		else:
			sent.append(s)
	
	return sent		


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.rstrip() + '\n')
	out_f.close()		


def get_smatch_max_length(gold_f, produced_f, threshold, root, epoch, id_num):
	produced = [x.strip() for x in open(produced_f, 'r')]		#output should be in one-line!
	keep_produced = []
	keep_gold = []
	cur_amr = []
	amr_idx = 0
	
	for line in open(gold_f, 'r'):
		if line.startswith('# ::snt'):
			sent_line = line.strip()
			sent_spl = line.replace('# ::snt','').strip().split()
			sent = filter_sent(sent_spl)

		elif line.startswith('#'):
			continue
		elif not line.strip():
			if len(sent) <= threshold:
				keep_gold.append(sent_line)
				keep_gold += cur_amr
				keep_gold.append('')
				keep_produced.append(produced[amr_idx])
			cur_amr = []
			amr_idx += 1	
		else:
			cur_amr.append(line)
	
	assert(len(keep_produced) == len([x for x in keep_gold if x.startswith('# ::snt')]))	#sanity check
	
	prod_file = root + '/prod_maxlen_{0}.txt'.format(threshold)
	gold_file = root + '/gold_maxlen_{0}.txt'.format(threshold)
	
	write_to_file(keep_produced, prod_file)
	write_to_file(keep_gold, gold_file)
	
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r {2} --one_line -f {0} {1}'.format(prod_file, gold_file, args.rs)
	f_score, num_sen = do_smatch(os_call, False)
	
	print 'Ep {3} {4}, max len {0}: {1} with {2} sent'.format(threshold, f_score, num_sen, epoch, id_num)
	
def evaluate(gold_f, produced_f, epoch, res_dict, id_num, root_fix):
	'''Will print smatch scores for Seq2seq checkpoints'''
	
	one_line = '--one_line'
	
	print_m = '{0} epochs {1}:'.format(epoch, id_num)
	num_tabs = '\t' * int(((8*4) - len(print_m)) / 8)
		
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r {3} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.rs)
	f_score, num_sen = do_smatch(os_call, False)
	res_dict.append([epoch, '{0}{1} {2}'.format(print_m, num_tabs, f_score)])
	
	#if epoch == 16 and id_num == '.seq.amr.restore.pruned.wiki.coref.all':
	#	for thres in range(1,50):		
	#		get_smatch_max_length(gold_f, produced_f, thres, root_fix, epoch, id_num)
								
	return res_dict


if __name__ == '__main__':
	#ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.wiki.coref']
	#ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.wiki.coref','.seq.amr.restore.wiki.coref']
	#ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.coref', '.seq.amr.restore.pruned', '.seq.amr.restore.pruned.wiki.coref.all']
	ids = ['.seq.amr.restore']
	
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
						res_dict = evaluate(args.g, f_path, epoch, res_dict, id_num, root_fix)
	
	res_dict.sort(key=lambda x: x[0])
	for l in res_dict:
		print l[1]					
