#!/usr/bin/env python

from sys import argv
import os
import codecs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d",required = True, type=str, help="folder that contains the amrs")
parser.add_argument("-raw_ext",required = False, default = ".txt", type=str, help="Input extension of raw files")
parser.add_argument("-check_ext",required = False, default = ".tok.charniak.parse", type=str, help="Extra extension to check for lines")
parser.add_argument("-min_lines",required = True, type=int, help="Minimum number of lines for -check_ext file")
args = parser.parse_args()

'''Deletes unfinished CAMR preprocessing parts'''

if __name__ == '__main__':
    for root, dirs, files in os.walk(args.d):
		for f in files:
			if f.endswith('.txt'):
				check_f = os.path.join(root, f) + args.check_ext
				if os.path.isfile(check_f):
					num_lines = len([x for x in open(check_f,'r')])
					if num_lines < args.min_lines:
						os_call = 'rm {0}.*'.format(os.path.join(root, f))
						os.system(os_call)
					#else:
					#	print 'Correct file'	
				else:
					os_call = 'rm {0}.*'.format(os.path.join(root, f))
					os.system(os_call)
