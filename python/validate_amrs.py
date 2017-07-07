#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Scripts that removes, rewrites or shows invalid AMRs'''

import re,sys, argparse, os, subprocess, json
import validator_seq2seq
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="AMR-file")
parser.add_argument("-r", required = True, choices=['rewrite', 'remove','show'], type =str, help="rewrite, remove or show AMRs?")
parser.add_argument("-o", required = False, default = '',  type=str, help="output-file for removed/rewritten AMRs")
args = parser.parse_args()


def get_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	return default


def check_valid(restore_file, arg_r, f_out):
	'''Checks whether the AMRS in a file are valid, possibly rewrites to default AMR'''
	
	idx = 0
	warnings = 0
	all_amrs = []
	for line in open(restore_file,'r'):
		idx += 1
		if not validator_seq2seq.valid_amr(line):
			warnings += 1
			if arg_r == 'rewrite':
				default_amr = get_default_amr()
				all_amrs.append(default_amr)		## add default when error
			elif arg_r == 'show':
				print line,'\n'
			#else remove, so don't do anything		
		else:
			all_amrs.append(line)
	
	print '{0} out of {1} AMRs are invalid'.format(warnings, idx)
	
	if f_out:
		with open(f_out, 'w') as out_f:
			for a in all_amrs:
				out_f.write(a.strip() + '\n')
		out_f.close()		
					

if __name__ == '__main__':
	check_valid(args.f, args.r, args.o)
	
