#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os, json
from collections import Counter

'''Find usual type of words. Input is assumed to be in .tf format'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File with AMRs")
parser.add_argument("-o", required=True, type=str, help="Ouput-file")
parser.add_argument("-c", default = 0.95, type=float, help="Confidence")
parser.add_argument("-l", default = 20, type=float, help="Minimum length")
args = parser.parse_args()

#(decrease-01 :ARG0 (silence-01 :ARG1 (protein :name (name :op1 "serpinE2")) :mod (gene)) :ARG1 (and 


def most_common(lst):
    return max(set(lst), key=lst.count)


if __name__ == '__main__':
	
	d = {}
	
	for line in open(args.f,'r'):
		pairs = re.findall(r' :[^ ]+ [^ ]+',line)
		pairs = [p.strip() for p in pairs]
		for p in pairs:	
			rel = p.split()[0]
			word = p.split()[1]
			word = re.sub(r'[\(\)\"]+','',word)
			if word in d:
				d[word].append(rel)
			else:
				d[word] = [rel]	
	
	res = []
	
	dict_out = {}
	
	for k in d:
		
		most_common_count = most_common(d[k])
		freq = float(d[k].count(most_common_count)) / float(len(d[k]))
		if freq >= args.c and len(d[k]) > args.l:
			dict_out[k] = [k, most_common_count, freq, len(d[k])]
			#res.append([k, d[k][0], freq, len(d[k])])
			#print k, d[k][0], len(d[k]), freq
		
		#res.sort(key=lambda x: (x[2], x[3]))
		
	#for r in res:
	#	print r[0], r[1], r[2],r[3]
	
	dict_name =  args.o + '_' + str(args.c) + '_' + str(int(args.l)) + '.txt'
	
	with open(dict_name, 'w') as fp:
		json.dump(dict_out, fp)			
