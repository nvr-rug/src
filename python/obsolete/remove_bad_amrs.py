#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Removing AMRs that do not fit the criteria'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File with AMRs")
parser.add_argument("-o", required=True, type=str, help="Output-file for filtered AMRs")
parser.add_argument("-min_tok", default = 3 , type=int, help="Min of average token length")
parser.add_argument("-long_thres", default = 4, type=int, help="Long word is at least this number of tokens")
parser.add_argument("-num_long", default = 4, type=int, help="At least this number of long-words should be in AMR sent")
args = parser.parse_args()


def get_avg_tok_length(line):
	tok_lengths = [len(x) for x in line.split()]
	avg_tok_length = float(sum(tok_lengths)) / float(len(tok_lengths))
	
	return avg_tok_length


def get_num_long_words(line, threshold):
	long_words = [x for x in line.split() if (len(x) >= threshold and all(y.isalpha() for y in x))]
	
	return len(long_words)


def nice_amr(line):
	avg_tok_length = get_avg_tok_length(line)
	num_long_words = get_num_long_words(line, args.long_thres)
		
	if avg_tok_length > args.min_tok and num_long_words >= args.num_long:
		#print line
		return True
	else:
		#print line
		return False	


def write_to_file(f, lst):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.rstrip() +'\n')
	out_f.close()	


if __name__ == '__main__':	
	all_amrs = []
	cur_amr = []
	
	filtered, not_filtered = 0,0
	
	for line in open(args.f,'r'):
		if line.startswith('# ::'):
			cur_amr.append(line)
		elif not line.strip():
			cur_amr_line = " ".join(cur_amr[2:])
			sent = cur_amr[1].replace('# ::snt','').strip()
			if nice_amr(sent.strip()):
				all_amrs += cur_amr 
				all_amrs.append('')
				not_filtered += 1
			else:
				filtered += 1	
			cur_amr = []        
		else:
			cur_amr.append(line)
	
	print 'Filter {0} out of {1} AMRs'.format(filtered, not_filtered + filtered)
	
	write_to_file(args.o, all_amrs)		
	
			
