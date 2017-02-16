#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that sets input files in char-level, but keeps structure words as single "char", e.g. :domain, :ARG1, :mod, etc'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.sent',  required=False, type=str, help="Input extension of AMRs (default .sent)")
parser.add_argument("-output_ext", default = '.tf', required=False, type=str, help="Output extension of AMRs (default .tf)")
args = parser.parse_args()


def get_file_lines(f_path):
	file_lines = []
	for line in open(f_path,'r'):
		line = line.replace(' ','+') #replace actual spaces with '+'
		new_l = ''
		add_space = True
		for idx, ch in enumerate(line):
			
			if ch == ':' and line[idx+1].isalpha():		#after ':' there should always be a letter, otherwise it is some URL probably and we just continue
				add_space = False
				new_l += ' ' + ch
			elif ch == '+':
				add_space = True
				new_l += ' ' + ch
			else:
				if add_space:
					new_l += ' ' + ch
				else:					#we previously saw a ':', so we do not add spaces
					new_l += ch	
		file_lines.append(new_l)
	
	return file_lines	
	

def get_fixed_lines(file_lines):
	fixed_lines = []
				
	for line in file_lines:
		spl = line.split()
		for idx, item in enumerate(spl):
			if len(item) > 1 and item[0] == ':':
				if any(x in item for x in [')','<',')','>','/','jwf9X']):		#filter out non-structure words, due to links etc
					new_str = ''
					for ch in item:
						new_str += ch + ' '
					spl[idx] = new_str.strip()
		fixed_lines.append(" ".join(spl))
	
	return fixed_lines	


def process_pos_tagged(f_path):
	fixed_lines = []
	
	
	for line in open(f_path, 'r'):
		new_l = ''
		no_spaces = False
		line = line.replace(' ','+') #replace actual spaces with '+'
		
		for idx, ch in enumerate(line):
			if ch == '|':
				no_spaces = True	#skip identifier '|' in the data
				new_l += ' '
			elif ch == ':' and line[idx-1] == '|':	#structure words are also chunks
				no_spaces = True
			elif ch == '+':
				no_spaces = False
				new_l += ' ' + ch
			elif no_spaces: #and (ch.isupper() or ch == '$'):		#only do no space when uppercase letters (VBZ, NNP, etc), special case PRP$	(not necessary)
				new_l += ch
			else:
				new_l += ' ' + ch
		fixed_lines.append(new_l)
	
	return fixed_lines					

	
if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:							
			f_path = os.path.join(root, f)		
			if f.endswith(args.output_ext) and 'char' not in f :				#keep structure words as "chars" for .tf files
				file_lines  = get_file_lines(f_path)
				fixed_lines = get_fixed_lines(file_lines)
				
				out_f =  f_path.replace(args.output_ext,'.char' + args.output_ext)
				
				with open(out_f, 'w') as out:
					for l in fixed_lines:
						out.write(l.strip() + '\n')
				out.close()
			
			elif '.pos' in f and '.sent' in f and 'char' not in f:						#different approach for pos-tagged sentences
				print 'POS tagged process'
				fixed_lines = process_pos_tagged(f_path)
				
				out_f =  f_path.replace(args.input_ext,'.char' + args.input_ext)
				
				with open(out_f, 'w') as out:
					for l in fixed_lines:
						out.write(l.strip() + '\n')
				out.close()
					
			elif f.endswith(args.input_ext) and 'char' not in f:						#do normal char-level approach for sentence files
				os_call =  'sed -e "s/\ /+/g"  -e "s/./&\ /g" < {0} > {1}'.format(f_path, f_path.replace(args.input_ext,'.char' + args.input_ext))
				os.system(os_call)
