#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Script that converts all recursively found AMR files to single line AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument("-d", required=True, type=str, help="data root")
parser.add_argument('-w', required = True,type=str, help="working directory (output)")
args = parser.parse_args()

if __name__ == "__main__":
	for root, dirs, files in os.walk(args.d):
		for fname in files:
			f_path = os.path.join(root,fname)
			print f_path
			if fname.endswith('.txt') and fname.startswith('deft-p2-amr-r2-amrs-'):
				os_call = 'python single_line_amr.py -d -f {0} -o {1}{2} -tf {1}{3}'.format(f_path, args.w, fname.replace('.txt','.sl'), fname.replace('.txt','.tf'))
				os.system(os_call)
