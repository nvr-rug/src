import os
import sys
import argparse
import re

'''Change CAMR file to one-line AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="sentence file that needs feature")
args = parser.parse_args()

if __name__ == '__main__':
	
	all_amrs = []
	cur_amr = []
	for line in open(args.f,'r'):
		if not line.strip():
			cur_amr_line = " ".join(cur_amr)
			all_amrs.append(cur_amr_line.strip())
			cur_amr = []
		elif not line.startswith('# ::'):
			cur_amr.append(line.strip())
	
	with open(args.f + '.ol','w') as out_f:
		for l in all_amrs:
			out_f.write(l.rstrip() + '\n')
	out_f.close()				
