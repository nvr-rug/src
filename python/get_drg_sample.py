#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that gets sample of DRGs to work with'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with all files")
parser.add_argument("-o", required=True, type=str, help="output_file")
parser.add_argument("-ext", default = 'en.drg', type=str, help="Directory with all files")
args = parser.parse_args()

def write_to_file(lst, f):
	with open(f, 'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		


if __name__ == "__main__":
	all_drgs = []
	count = 0
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.ext):
				drg = [x.strip() for x in open(os.path.join(root,f),'r')]
				
				if ' ]' not in " ".join(drg) and '<triple>' not in " ".join(drg): #and len(drg) < 100:
					all_drgs.append('')
					all_drgs += drg
					count += 1
					if count % 1000 == 0:
						print os.path.join(root, f), count, len(all_drgs)
					if count % 10000 == 0:
						write_to_file(all_drgs, args.o)	#write to file already as a backup
	
	write_to_file(all_drgs, args.o)
					
