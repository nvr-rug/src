#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,re,argparse, os, json, subprocess
from collections import Counter
import validator_seq2seq

'''Find usual type of words. Input is assumed to be in .tf format'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File with AMRs")
parser.add_argument("-o", default = '.ct', type=str, help="Ouput-ext")
parser.add_argument("-d", required=True, type=str, help="Dict-file")
parser.add_argument("-g", default = '/home/p266548/Documents/amr_Rik/bio_data/amrs/test/bio_test_amrs.txt', type=str, help="Gold AMR file")
args = parser.parse_args()


def get_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	return default


def load_json_dict(d):
	
	with open(d, 'r') as fp:						# load in dictionary
		data_dict = json.load(fp)
	fp.close()
	
	return data_dict


def change_amrs(out_file):
	
	new_lines = []
	changes = 0
	
	for idx, line in enumerate(open(args.f, 'r')):
		pairs = re.findall(r' :[^ ]+ [^ ]+',line)
		pairs = [p.strip() for p in pairs]
		for p in pairs:	
			if len (p.split()) == 2:
				rel = p.split()[0]
				word = p.split()[1]
				word_sub = re.sub(r'[\(\)\"]+','',word)
				if word_sub in d:
					if rel != d[word_sub][1]:
						to_replace = (word + ' ' + rel).strip()
						replace_with = (word + ' ' + d[word_sub][1]).strip()
						try:
							line = line.replace(to_replace, replace_with)
							changes += 1
						except UnicodeDecodeError as e:
							print 'Unicode error for line {0}'.format(idx)
							print to_replace
							print replace_with,'\n'
	
		new_lines.append(line)						
	
	print 'Made {0} changes'.format(changes)					
	
	with open(out_file,'w') as out_f:
		for n in new_lines:
			out_f.write(n.strip() + '\n')


def restore_amrs(in_file):
	os_call = 'python /home/p266548/Documents/amr_Rik/Seq2seq/src/python/restoreAMR/restore_amr.py {0} > {1}'.format(in_file, in_file + '.restore')
	os.system(os_call)


def check_valid(restore_file, rewrite):
	'''Checks whether the AMRS in a file are valid, possibly rewrites to default AMR'''
	
	idx , warnings = 0,0 
	all_amrs = []
	for idx, line in enumerate(open(restore_file,'r')):
		if not validator_seq2seq.valid_amr(line):
			print 'Error or warning in line {0}, write default\n'.format(idx + 1)
			warnings += 1
			default_amr = get_default_amr()
			all_amrs.append(default_amr)		## add default when error
		else:
			all_amrs.append(line)	
	
	if warnings == 0:
		print 'No badly formed AMRs!\n'
	elif rewrite:
		print 'Rewriting {0} AMRs with error to default AMR\n'.format(warnings)
		
		with open(restore_file,'w') as out_f:
			for line in all_amrs:
				out_f.write(line.strip()+'\n')
		out_f.close()		
	else:
		print '{0} AMRs with warning - no rewriting to default\n'.format(warnings)


def smatch_test(prod_file, gold_file):
	smatch_call = 'python /home/p266548/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py --one_line -f {0} {1}'.format(prod_file, gold_file)
	output = subprocess.check_output(smatch_call, shell=True)
	f_score = output.split()[-1]		# get F-score from output
	print 'F-score:', f_score
	return f_score

if __name__ == '__main__':
	d = load_json_dict(args.d)
	
	changed_amrs  = change_amrs(args.f + args.o)		# change type of AMRs based on dictionary
	restore_amrs(args.f + args.o) 						# restore the AMRs after
	check_valid(args.f + args.o + '.restore', True)		# check if they were valid (if not: rewrite to default)
	f_score_new = smatch_test(args.f + args.o + '.restore', args.g)	# check if we improved using smatch
	f_score_old = smatch_test(args.f + '.restore', args.g)	
