#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os
import subprocess

'''Script calculates smatch for AMRs with and without coreference nodes'''

parser = argparse.ArgumentParser()
parser.add_argument("-f1", required=True, type=str, help="Prod file (dev) or prod folder (test)")
parser.add_argument("-f2", required=True, type=str, help="Gold file")
parser.add_argument("-d", required=True, type=str, help="Folder for temp files")
parser.add_argument("-o", default = '.restore', type=str, help="Output ext of files we want to concatenate for test")
parser.add_argument('-t', action='store_true', help='Whether this is the test folder. If true, we have to create the test set again')
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		


def variable_match(spl, idx, no_var_list):
	'''Function that matches entities that are variables occurring for the second time'''
	if idx >= len(spl) or idx == 0:

		return False
	
 	if not spl[idx+1] == '/' and not spl[idx-1] == '/' and any(char.isalpha() for char in spl[idx]) and spl[idx] not in no_var_list and not spl[idx].startswith(':') and len([x for x in spl[idx] if x.isalpha() or x.isdigit()]) == len(spl[idx]) and (len(spl[idx]) == 1 or (len(spl[idx].strip()) > 1 and spl[idx][-1].isdigit())):
		return True
	else:
		return False


def has_coreference(line):
	'''Function that checks how many coreference nodes an AMR has'''
	
	spl = line.replace('(',' ( ').replace(')',' ) ').split()	# "tokenize" AMRs
	no_var_list = ['interrogative','expressive','imperative']	# we always skip stuff such as :mode interrogative as possible variables
	all_vars = []
	
	for idx in range(0, len(spl) -1):
		if variable_match(spl, idx, no_var_list): 		#check if entity looks like a coreference variable				
			all_vars.append(spl[idx])
	
	return len(set(all_vars))

def get_amrs(f):
	all_amrs = []
	cur_amr = []
	
	for line in open(f, 'r'):
		if not line.strip() and cur_amr:		#amr finished
			all_amrs.append(" ".join(cur_amr))
			cur_amr = []
		elif not line.startswith('#'):	#ignore comments
			cur_amr.append(line.strip())
	
	if cur_amr:
		all_amrs.append(" ".join(cur_amr))	
	
	return all_amrs		


def split_by_coref(prod_amrs, gold_amrs, cor_dir, ident):
	prod_coref = []
	prod_rest = []
	gold_coref = []
	gold_rest = []
	total_coref = 0
	
	for p, g in zip(prod_amrs, gold_amrs):
		coref_vars_num = has_coreference(g)
		if coref_vars_num > 0:
			prod_coref.append(p)
			gold_coref.append(g)
		else:	
			prod_rest.append(p)
			gold_rest.append(g)
		
		total_coref += coref_vars_num	
	
	print 'Total number of reentrancies: {0}'.format(total_coref)
	print 'Len prod coref: {0}\nLen gold coref: {1}\nLen prod rest: {2}\nLen gold rest: {3}\n'.format(len(prod_coref), len(gold_coref), len(prod_rest), len(gold_rest))

	write_to_file(prod_coref, cor_dir + 'prod_coref_' + ident)
	write_to_file(gold_coref, cor_dir + 'gold_coref_' + ident)
	write_to_file(prod_rest, cor_dir + 'prod_rest_' + ident)
	write_to_file(gold_rest, cor_dir + 'gold_rest_' + ident)
	
	return cor_dir + 'prod_coref_' + ident, cor_dir + 'gold_coref_' + ident, cor_dir + 'prod_rest_' + ident, cor_dir + 'gold_rest_' + ident

def get_amr_set(f1, f2):
	
	prod_amrs = [x.strip() for x in open(f1,'r')]	
	gold_amrs = [x.strip() for x in open(f2,'r')]	
	
	if len(prod_amrs) != len([x for x in prod_amrs if x]):		#check if AMRs are in one-line format or not, if so, read them again
		prod_amrs = get_amrs(args.f1)
	if len(gold_amrs) != len([x for x in gold_amrs if x]):	
		gold_amrs = get_amrs(args.f2)
	
	assert len(prod_amrs) == len(gold_amrs)
	
	return prod_amrs, gold_amrs


def do_smatch(f1, f2):
	call = ["python","/home/p266548/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py","-f", f1,f2,'-r', '20','--both_one_line']
	
	try:
		output = subprocess.check_output(call)
	except subprocess.CalledProcessError, e:
		print "Smatch error"
	
	f_score = re.findall(r'F-score: ([\d]+\.[\d]+)', output)[0]	
	
	return f_score


def create_gold_test(fol, cor_dir):
	out_file = '{0}all_test.out'.format(cor_dir)
	
	files = [os.path.join(fol,f) for f in os.listdir(fol) if os.path.isfile(os.path.join(fol, f)) and f.endswith(args.o) and 'average' not in f]
	sorted_files = sorted(files)
	
	cat_call = 'cat ' + " ".join(sorted_files) + ' > ' + out_file
	#print cat_call
	os.system(cat_call)
	
	return out_file

	
	
if __name__ == "__main__":
	os.system("mkdir -p {0}coref_split".format(args.d))
	cor_dir = "{0}coref_split/".format(args.d)
	
	if args.t:
		ident = 'test'
		prod_file = create_gold_test(args.f1, cor_dir)
	else:
		ident = 'dev'
		prod_file = args.f1	
	
	prod_amrs, gold_amrs = get_amr_set(prod_file, args.f2)
	
	prod_coref_f, gold_coref_f, prod_rest_f, gold_rest_f = split_by_coref(prod_amrs, gold_amrs, cor_dir, ident)
	
	f_score_coref = do_smatch(prod_coref_f, gold_coref_f)
	f_score_rest = do_smatch(prod_rest_f, gold_rest_f)
	
	print "F-score coref: {0}".format(f_score_coref)
	print "F-score rest: {0}".format(f_score_rest)
