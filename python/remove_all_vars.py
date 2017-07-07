#!/usr/bin/env python
# -*- coding: utf8 -*-

import re,sys, argparse, os, random, collections, subprocess, json
reload(sys)
import validator_seq2seq

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="File with AMRs (one line)")
parser.add_argument("-out_ext", default = '.txt.ol', type=str, help="Extension of output files")
args = parser.parse_args()

def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		

if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if 'char' not in f and f.endswith(args.out_ext):
				f_path = os.path.join(root, f)
				print f_path
				new_lines = []
				for line in open(f_path, 'r'):
					fixed_line = re.sub(r'\((.*?/)', '(', line).replace('( ', '(')		
					new_lines.append(fixed_line)
				
				#os.system('rm {0}'.format(f_path))
				write_to_file(new_lines, f_path + '.novar')
