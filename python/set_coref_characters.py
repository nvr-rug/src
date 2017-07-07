#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that changes the coref-characters in char-format to super-char, e.g. * 8 * to *8*'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory that contains the files")
parser.add_argument('-ext', required = False, default = '.char.tf', help="Extension of char files")
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		

if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.ext):
				f_path = os.path.join(root, f)
				print 'Converting {0}'.format(f_path)
				new_lines = []
				for line in open(f_path, 'r'):
					new_line = re.sub(r'\* (\d) \*',r'*\1*', line)		#make the change here
					new_line2 = re.sub(r'\* (\d) (\d) \*',r'*\1\2*', new_line)	
					new_lines.append(new_line2)
				
				write_to_file(new_lines, f_path)
