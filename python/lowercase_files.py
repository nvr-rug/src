#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Simply lowercase all files in directory and subdirectories(recursively)'''

parser = argparse.ArgumentParser()
parser.add_argument("-d", required=True, type=str, help="Starting directory")
args = parser.parse_args()


def to_lower_case(f):
	l =[x.lower() for x in open(f, 'r')]
	
	with open(f, 'w') as out_f:
		for item in l:
			out_f.write(item)
	out_f.close()		


if __name__ == '__main__':
	do_files = []
	for root, dirs, files in os.walk(args.d):
		for f in files:
			do_files.append(f)
	
	print 'Files to lowercase-replace:'
	for d in do_files:
		print d
	
	var = raw_input("\nIs this correct? Press y for yes.\n")
	if var == 'y':	
		for root, dirs, files in os.walk(args.d):
			for f in files:							
				f_path = os.path.join(root, f)
				#print f_path
				to_lower_case(f_path)
		print 'Finished lower-casing'
	else:
		print 'Incorrect, exiting...'			
