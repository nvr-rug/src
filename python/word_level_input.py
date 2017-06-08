#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that puts AMR-files in word-level input'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains the amrs")
parser.add_argument('-extension', required = False, default = '.tf', help="extension of AMR files (default .tf)")
parser.add_argument('-output_ext', required = False, default = '.char.tf', help="ext of output (default .char.tf")
args = parser.parse_args()


def process_file(f):
	new_lines = []
	for line in open(f, 'r'):
		split_l = " ".join(line.replace(')',' ) ').replace('(',' ( ').replace('"',' " ').replace("'"," ' ").split())
		print line
		print split_l,'\n'

if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.extension):
				process_file(os.path.join(root, f))
