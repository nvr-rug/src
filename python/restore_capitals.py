import sys
import re
import argparse
import os

'''Script that restores capitals in AMRs after aligner removed them'''

parser = argparse.ArgumentParser()
parser.add_argument('-l', required = True,help="Lower-case file with alignments")
parser.add_argument('-u', required = True,help="Upper-case file without alignments")
parser.add_argument('-o', required = True,help="Output upper-case file with alignments")
args = parser.parse_args() 


def write_to_file(lst, f):
	with open(f, 'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		


if __name__ == '__main__':
	lower = [x.strip() for x in open(args.l,'r')]
	upper = [x.strip() for x in open(args.u,'r')]
	
	assert len(lower) == len(upper)
	fixed_lines = []
	
	for idx in range(len(lower)):
		up_line = " ".join(upper[idx].replace('(',' ( ').replace(')',' ) ').split())						#to make our life easier,  repair this later
		low_line = " ".join(lower[idx].replace('~', ' ~').replace('(',' ( ').replace(')',' ) ').split())
		

		split_low = low_line.split()
		split_up = up_line.split()
		up_lowered = [x.lower() for x in split_up]
				
		new_amr = []
		for l in split_low:
			if l.startswith('~') or l == '(' or l == ')' or l.startswith('~'):	#these are never items that need capitals, skip
				new_amr.append(l)
			else:
				for i, u in enumerate(up_lowered):
					if u == l:									#current item matches with lowered item
						#print l, split_up[i]
						new_amr.append(split_up[i])				#so we add the one with capitals instead
						break
		
		new_line = " ".join(new_amr).replace(' ~','~')
		
		while '( ' in new_line or ' )' in new_line:						#repairing
			new_line = new_line.replace('( ','(').replace(' )',')')				
		
		if len(new_line) != len(lower[idx]):
			print 'Wrong length:', len(new_line), len(lower[idx])
			print new_line
			print lower[idx],'\n'
		
		fixed_lines.append(new_line)
	
	write_to_file(fixed_lines, args.o)
