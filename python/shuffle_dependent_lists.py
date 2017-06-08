#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Shuffle two files, but keep dependent order'''

import re,sys, argparse, os, subprocess, json
from random import shuffle
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-l", required = True, nargs=2, help="Number of files to be sorted")
parser.add_argument("-ext", default = '.shuffled', help="New extension")
parser.add_argument("-mx", default = 0, type = int, help="Max number of lines, 0 means no maximum")
args = parser.parse_args()

def write_to_file(lst, f):
	with open(f, 'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()


def shuffle_dependent_lists(lst1, lst2):
	assert(len(lst1) == len(lst2))
	
	num_list = [i for i in range(len(lst1))]	
	shuffle(num_list)						#random list of numbers
	new_lst1 = []
	new_lst2 = []
	
	for idx in num_list:
		new_lst1.append(lst1[idx])
		new_lst2.append(lst2[idx])
	
	return new_lst1, new_lst2


if __name__ == '__main__':
	f1 = [x.strip() for x in open(args.l[0],'r')]
	f2 = [x.strip() for x in open(args.l[1],'r')]
	
	print 'Reading files complete'
	
	l1,l2 = shuffle_dependent_lists(f1, f2)
	
	print 'Shuffling complete'
	
	if args.mx > 0:
		print 'Files have max length {0}'.format(args.mx)
		l1 = l1[0:args.mx]	#max number of lines
		l2 = l2[0:args.mx]
	else:
		print 'No maximum on number of lines'	
		
	write_to_file(l1, args.l[0] + args.ext)
	write_to_file(l2, args.l[1] + args.ext)
	
	print 'Writing output complete'
