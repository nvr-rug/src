#!/usr/bin/env python
# -*- coding: utf8 -*-

from sys import argv
import os
import codecs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f",required = True, type=str, help="Inputfile")
parser.add_argument("-o",required = True, type=str, help="Outputfile in UTF-8")
args = parser.parse_args()

'''Deletes unfinished CAMR preprocessing parts'''

if __name__ == '__main__':
	utf_8_lines = []
	for line in open(args.f, 'r'):
		valid_utf8 = True
		try:
			line.decode('utf-8')
		except UnicodeDecodeError:
			valid_utf8 = False
		
		if valid_utf8:
			utf_8_lines.append(" ".join(line.split()))
	
	with open(args.o, 'w') as out_f:
		for u in utf_8_lines:
			out_f.write(u.strip() + '\n')
	out_f.close()						
			
