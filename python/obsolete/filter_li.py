import os
import sys
import argparse
import re

'''Script that filters AMRs with li-1 or li "'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="AMR-file")
parser.add_argument("-o", required=True, type=str, help="AMR-output file")
args = parser.parse_args()


if __name__ == '__main__':
	new_lines = []
	skipped = 0
	cur_amr = []
	total = 0
	for line in open(args.f,'r'):
		if not line.strip():
			text_amr = [x for x in cur_amr if not x.startswith('#')]
			txt = " ".join(text_amr)
			
			if ':li "' in txt or ':li -' in txt:
				skipped += 1	
			else:
				new_lines += cur_amr
				new_lines.append('')
			
			cur_amr = []
			total += 1		
		else:
			cur_amr.append(line)

print len(new_lines)	
print 'Skipped {0} out of {1}'.format(skipped, total)

with open (args.o, 'w') as out_f:
	for n in new_lines:
		out_f.write(n.rstrip() + '\n')
out_f.close()		
