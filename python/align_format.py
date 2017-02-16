import os
import sys
import argparse
import re

'''Scripts that puts AMR file in Align format'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File with AMRs")
parser.add_argument("-out_amr", required=True, type=str, help="File with AMRs")
parser.add_argument("-out_sent", required=True, type=str, help="File with AMRs")
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		


if __name__ == '__main__':
	sents = []
	all_amrs = []
	cur_amr = []
	
	for line in open(args.f,'r'):
		#print line
		if line.startswith('# ::tok'):
			add_line = line.replace('# ::tok','').strip()
			sents.append(add_line)
		elif line.startswith('# ::'):
			continue
		elif not line.strip():
			cur_amr_line = " ".join(cur_amr)
			all_amrs.append(cur_amr_line)
			cur_amr = []
		else:
			cur_amr.append(line.strip())			
	
	#for l in all_amrs:
	#	print l.rstrip()
	
	
	write_to_file(sents, args.out_sent)
	write_to_file(all_amrs, args.out_amr)		
