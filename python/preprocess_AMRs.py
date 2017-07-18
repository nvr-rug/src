#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that preprocess all AMRs - best permutation, doubling, POS-tagged, char-level, etc'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory that contains AMRs")
parser.add_argument("-sent_ext", default = '.sent',  required=False, type=str, help="Sent extension (default .sent)")
parser.add_argument("-raw_ext", default = '.txt', required=False, type=str, help="Raw extension of AMRs (default .txt)")
parser.add_argument("-amr_ext", default = '.tf', required=False, type=str, help="Extension of AMRs (default .tf)")
parser.add_argument('-best', action='store_true', help='Changing AMRs to best permutation')
parser.add_argument('-double', action='store_true', help='Doubling the AMR input (best + normal permutation)')
parser.add_argument('-pos', action='store_true', help='Whether input is POS-tagged')
parser.add_argument('-super', action='store_true', help='Whether we want super characters')
args = parser.parse_args()


if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:							
			if f.endswith(args.amr_ext):	
				f_path = os.path.join(root, f)
				
				if args.best:
				
				elif args.double:
				
				else:		
				
				
