#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that gets sample of DRGs to work with'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Drg file")
args = parser.parse_args()

if __name__ == "__main__":
	new_lines = []
	prev = False
	counter = 0
	for line in open(args.f,'r'):
		counter += 1
		if line.startswith('%'):
			if prev:
				new_lines.append(line)
			else:
				new_lines.append('')
				new_lines.append(line)
				new_lines.append('')
			prev = True		
		else:
			prev = False
			new_lines.append(line)
	
	prev = False
	
	for l in new_lines:
		if not l.strip():
			if not prev:
				print l.strip()
			prev = True
		else:
			prev = False	
			print l.strip()
