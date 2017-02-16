import os
import sys
import argparse
import re

'''Script that filters AMRs with non-matching number of parentheses'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="AMR-file")
parser.add_argument("-o", required=True, type=str, help="Output AMR-file")
args = parser.parse_args()

if __name__ == '__main__':
	new_lines = []
	skipped = 0
	cur_amr = []
	#with open(args.o, 'w') as f:
	for line in open(args.f,'r'):
		if not line.strip():
			text_amr = [x for x in cur_amr if not x.startswith('#')]
			txt = " ".join(text_amr)
			print txt.count(')'), txt.count('(')
			if txt.count(')') != txt.count('('):
				
				print 'Skip this AMR'
				skipped += 1
			#else:
			#	for c in cur_amr:
			#		print c.rstrip()
					#f.write(c)
			cur_amr = []		
		else:
			cur_amr.append(line) 
