#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Scripts rewrites brackets to specific-level bracket chars in AMRs'''

import re,sys, argparse, os, subprocess, json
import validator_seq2seq
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="Working folder with AMRs")
parser.add_argument("-input_ext", required = False, default = '.tf',  type=str, help="Input extension (default .tf)")
parser.add_argument("-add_ext", required = False, default = '.brack',  type=str, help="New added extension to the output file")
args = parser.parse_args()

def restore_paren(line):
	new_line = re.sub(r'\*\d(\d+)?\(\*',r'(',line)
	new_line = re.sub(r'\*\d(\d+)?\)\*',r')',new_line)
	return new_line.strip()
	
def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		


def add_bracket_chars(f):
	new_amrs = []
	for l in open(f, 'r'):
		new_line = ''
		level = 1
		line = l.strip()[1:-1]	#remove starting and closing brackets, those are unnecesarry and can be added in restoring anyway
		for ch in line:
			if level < 0:
				print 'Should not happen, bracket level < 0'
	
			if ch == '(':
				if level <= 10:
					new_line += '*{0}(*('.format(level)
				else:
					new_line += '*100(*('
				level += 1
			elif ch == ')':
				level -= 1
				if level <= 10:
					new_line += '*{0})*)'.format(level)
				else:	
					new_line += '*100)*)'

				
			else:
				new_line += ch
		#check_line = restore_paren(new_line) #possible check to see if lines are similar after restoring
		new_amrs.append(new_line)
	return new_amrs					

if __name__ == '__main__':

	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.input_ext) and args.add_ext not in f:
				f_path = os.path.join(root, f)
				new_amrs = add_bracket_chars(f_path)
				new_file = f_path + args.add_ext
				write_to_file(new_amrs, new_file)
