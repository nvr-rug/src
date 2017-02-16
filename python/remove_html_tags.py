import os
import sys
import argparse
import re

'''Script that removes HHTML tags from sentences'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with files with AMRs")
parser.add_argument("-g", required=True, type=str, help="Directory with files with AMRs")
parser.add_argument("-amr_ext", default = '.txt', type=str, help="AMR extension")
args = parser.parse_args()


def remove_tags(line):
	new_l =  re.sub('<[^<]+?>', '', line)
	return new_l


def process_file(f):
	new_lines = []
	
	for line in open(f,'r'):
		if line.startswith('# ::tok') or line.startswith('# ::snt'):
			new_line = remove_tags(line)
			new_lines.append(new_line)
			#print new_line.rstrip()
		else:
			new_lines.append(line)
			#print line.rstrip()
	
	with open(f,'w') as out_f:
		for l in new_lines:
			out_f.write(l.rstrip() + '\n')			

if __name__ == '__main__':
	
	process_file(args.f)
		
	#for root, dirs, files in os.walk(args.f):
	#	for f in files:
	#		if f.endswith(args.amr_ext):
	#			f_path = os.path.join(root, f)
	#			process_file(f_path)
	
