import os
import sys
import argparse
import time

'''Script that removes some words from the sentence based on their POS-tags'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with files with postagged sentences")
parser.add_argument("-pos_ext", default = '.sent.pos', type=str, help="POS extension")
args = parser.parse_args()


def print_to_file(print_list, f):
	with open(f,'w') as out_f:
		for line in print_list:
			out_f.write(line.strip() + '\n')


def process_file(f):
	remove_tags = ['RRB','LRB',':','RQU','LQU', 'EX', 'WDT','DT']
	idx = 0
	new_lines = []
	
	for line in open(f, 'r'):
		idx += 1
		spl_line = line.split()
		keep_words = []
		for w in spl_line:
			if '|' in w:
				pos_tag = w.split('|')[-1].strip()
				if pos_tag not in remove_tags and w != '?|.':
					keep_words.append(w)
		new_lines.append(" ".join(keep_words))
	
	assert (len(new_lines) == idx)
	
	return new_lines				

if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.pos_ext) and 'char' not in f:
				f_path = os.path.join(root, f)
				new_lines = process_file(f_path)
				print_to_file(new_lines, f_path)
