#!/usr/bin/env python

import os
import re
import sys
import argparse

'''Script lets you find good AMR examples'''

parser = argparse.ArgumentParser()
parser.add_argument('-f', required=True, type=str, help="AMR file")
parser.add_argument('-l', required=True, type=int, help="Max AMR len")

args = parser.parse_args()


def print_matching_amrs(input_f, max_lines):    
	cur_amr = []
	has_content = False
	var_present = 0
	wiki_present = False
	quant_present = False
	
	for line in open(input_f,'r'):
		if line.strip() == "":
			if not has_content:
				continue
			else: 
				if len(" ".join(cur_amr)) < 35 and " ".join(cur_amr).count(':') == 2 and len(cur_sent.split()) > 1:
				#if (len(cur_amr) <= max_lines):# and var_present > 0 and wiki_present: #and quant_present:
					print cur_sent
					for c in cur_amr:
						print c
					print '\n'	
					
				cur_amr = []
				has_content = False
				var_present = 0
				wiki_present = False
				quant_present = False
				continue
		if line.strip().startswith("#"):
			if line.strip().startswith('# ::snt'):
				cur_sent = line.replace('# ::snt','').strip()
				#if len(cur_sent.split())< 6 and len(cur_sent.split()) > 2 and len(cur_sent) < 20:
				#	print cur_sent
			continue
		else:
			has_content = True
			cur_amr.append(line.rstrip())
			if '/' not in line:
				var_present += 1
			if ':wiki' in line and ':wiki -' not in line:
				wiki_present = True
			if ':quant' in line:
				quant_present = True		
	
if __name__ == '__main__':
	print_matching_amrs(args.f, args.l)
