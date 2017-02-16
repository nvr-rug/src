import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.sent',  required=False, type=str, help="Input extension of AMRs (default .sent)")
parser.add_argument("-output_ext", default = '.tf', required=False, type=str, help="Output extension of AMRs (default .tf)")
args = parser.parse_args()


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


for root, dirs, files in os.walk(args.f):
	for f in files:
		if (f.endswith(args.input_ext) or f.endswith(args.output_ext)) and '.char' not in f:
			if '.pos' in f and '.sent' in f:						#different approach for pos-tagged sentences
				f_path = os.path.join(root, f)
				fixed_lines = process_pos_tagged(f_path)
				
				out_f =  f_path.replace(args.input_ext,'.char' + args.input_ext)
				
				with open(out_f, 'w') as out:
					for l in fixed_lines:
						out.write(l.strip() + '\n')
				out.close()
			else:
				f_path = os.path.join(root, f)
				os_call =  'sed -e "s/\ /+/g"  -e "s/./&\ /g" < {0} > {1}'.format(f_path, f_path.replace(args.input_ext,'.char' + args.input_ext).replace(args.output_ext,'.char' + args.output_ext))
				os.system(os_call)
