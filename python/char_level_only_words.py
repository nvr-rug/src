#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that sets input files in char-level, but keeps structure words as single "char", e.g. :domain, :ARG1, :mod, etc'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
#parser.add_argument("-brackets", default = '', type=str, help="Do we see multiple brackets as a single character?")
parser.add_argument("-input_ext", default = '.sent',  required=False, type=str, help="Input extension of AMRs (default .sent)")
parser.add_argument("-output_ext", default = '.tf', required=False, type=str, help="Output extension of AMRs (default .tf)")
parser.add_argument("-coref", default = '', required=False, type=str, help="Include if we did something with coreference")
args = parser.parse_args()


#def bracket_lines(lines):
	#new_lines = []
	#for l in lines:
		#while ') )' in l:
			#l = l.replace(') )','))')
		#add_l = " ".join(l.split()) #remove double spaces
		#new_lines.append(add_l)
	
	#return new_lines		


def write_to_file(lst, f):
	with open(f, 'w') as out:
		for l in lst:
			out.write(l.strip() + '\n')
	out.close()


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
	'''Fix lines, filter out non-relation for example'''
	
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
	
	### Step that is coreference-specific: change | 1 | to |1|, as to not treat the indexes as normal numbers, but as separate super characters
	
	if args.coref:
		new_lines = []
		for l in fixed_lines:
			new_l = re.sub(r'\| (\d) \|',r'|\1|', l)
			new_lines.append(new_l)
		return new_lines	
	else:		
			
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


def set_brack_lines(lst): 
	new_list = []
	for l in lst:
		new_l = re.sub(r'\* (\d) \( \*', r'*\1(*',l)
		new_l = re.sub(r'\* (\d) \) \*', r'*\1)*',new_l)

		new_l = re.sub(r'\* (\d) (\d) \( \*', r'*\1\2(*',new_l)
		new_l = re.sub(r'\* (\d) (\d) \) \*', r'*\1\2)*',new_l)

		new_l = re.sub(r'\* (\d) (\d) (\d) \( \*', r'*\1\2\3(*',new_l)
		new_l = re.sub(r'\* (\d) (\d) (\d) \) \*', r'*\1\2\3)*',new_l)
		
		new_list.append(new_l)
	return new_list	

	
if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:							
			f_path = os.path.join(root, f)		
			if (f.endswith(args.input_ext) or f.endswith(args.output_ext)) and '.char' not in f:
				if f.endswith('.tf'):				#keep structure words as "chars" for .tf files
					file_lines  = get_file_lines(f_path)
					fixed_lines = get_fixed_lines(file_lines)
					out_f =  f_path.replace('.tf','.char.tf')
					write_to_file(fixed_lines, out_f)
				elif f.endswith('.tf.brack') or f.endswith('.tf.brackboth'):							#bracketed files should keep *1(* etc as single character
					file_lines  = get_file_lines(f_path)
					fixed_lines = get_fixed_lines(file_lines)
					brack_lines = set_brack_lines(fixed_lines)
					out_f =  f_path.replace('.tf.brack','.char.tf.brack')
					write_to_file(brack_lines, out_f)	
				
				elif f.endswith('.sent.pos'):					#different approach for pos-tagged sentences
					print 'POS tagged process'
					fixed_lines = process_pos_tagged(f_path)
					out_f =  f_path.replace('.sent.pos','.char.sent.pos')
					write_to_file(fixed_lines, out_f)
						
				elif f.endswith('.sent'):					#do normal char-level approach for sentence files
					os_call =  'sed -e "s/\ /+/g"  -e "s/./&\ /g" < {0} > {1}'.format(f_path, f_path.replace('.sent','.char.sent'))
					os.system(os_call)
				else:
					print 'Both extensions not found, skipping {0}'.format(f)	
