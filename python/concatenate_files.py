#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script that concatenates all files in folder based on extension and prefix
   Is used for concatenating sentence and AMR files when they were split for
   parallel processing, e.g part1.tf and part.sent'''

import re,sys, argparse, os
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-d", required = True, type=str, help="Directory with the files")
parser.add_argument("-ext1", default = '.sent.fil', type=str, help="First extension")
parser.add_argument("-ext2", default = '.seq.amr.restore.check.pruned.coref.all', type=str, help="Second extension")
args = parser.parse_args()



def write_to_file(lst, f):
	with open(f, 'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()	


if __name__ == '__main__':
	lst1 = []
	lst2 = []
	
	for root, dirs, files in os.walk(args.d):
		for f in files:
			if f.endswith(args.ext1):
				f1 = os.path.join(root, f)
				f2 = f1.replace(args.ext1, args.ext2)
				if not os.path.isfile(f2):
					print '{0} has no counterpart, skipping'.format(f)
				else:
					lst1 += [x.strip() for x in open(f1, 'r')] 	
					lst2 += [x.strip() for x in open(f2, 'r')] 	
	
	print 'Writing to file with len {0} and {1}'.format(len(lst1), len(lst2))
	
	write_to_file(lst1, 'all' + args.ext1)
	write_to_file(lst2, 'all' + args.ext2)
