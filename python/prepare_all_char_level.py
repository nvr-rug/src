import os
import sys
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.sent',  required=False, type=str, help="Input extension of AMRs (default .sent)")
parser.add_argument("-output_ext", default = '.tf', required=False, type=str, help="Output extension of AMRs (default .tf)")
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f, 'w') as out:
		for l in lst:
			out.write(l.strip() + '\n')
	out.close()


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


def get_char_lines(f):
	#set lines in initial easy char-level
	
	char_lines = []
	for line in open(f,'r'):
		new_l = " ".join(line.strip().split()).replace(' ', '+')
		char_line = " ".join([x for x in new_l]).strip()
		char_lines.append(char_line)
	
	return char_lines

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


for root, dirs, files in os.walk(args.f):
	for f in files:
		if (f.endswith(args.input_ext) or f.endswith(args.output_ext)) and '.char' not in f:
			f_path = os.path.join(root, f)
			if '.pos' in f and '.sent' in f:						#different approach for pos-tagged sentences
				fixed_lines = process_pos_tagged(f_path)
				
				out_f =  f_path.replace(args.input_ext,'.char' + args.input_ext)
				write_to_file(fixed_lines, out_f)
				
			elif f.endswith('.tf.brack') or f.endswith('.tf.brackboth'):
				char_lines = get_char_lines(f_path)
				brack_lines = set_brack_lines(char_lines)
				out_f =  f_path.replace('.tf.brack','.char.tf.brack')
				write_to_file(brack_lines, out_f)	
			
			else:
				os_call =  'sed -e "s/\ /+/g"  -e "s/./&\ /g" < {0} > {1}'.format(f_path, f_path.replace(args.input_ext,'.char' + args.input_ext).replace(args.output_ext,'.char' + args.output_ext))
				os.system(os_call)
