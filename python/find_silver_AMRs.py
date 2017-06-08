#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Find AMRs again after we lost the initial format by making it char-level'''

import re,sys, argparse, os, subprocess, json
from random import shuffle
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-d", required = True, type=str, help="Dictionary file with smatch results")
parser.add_argument("-s", required = True, type=str, help="Sentence file")
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f, 'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		



if __name__ == '__main__':
	#with open(args.d) as in_f:    
		#d = json.load(in_f)
	
	#sents = [s.strip() for s in open(args.s,'r')]
	
	#data = {}
	
	#for key in d:
		#data[key.replace('# ::snt ','').strip()] = d[key]
	
	#amrs = []
	
	#for s in sents:
		#if s in data:
			#get_amr = data[s][0]
			#amrs.append(get_amr)		
		#else:
			#print 'This should not happen'		
	
	#print 'Length AMRs: {0}'.format(len(amrs))
	
	#write_to_file(amrs, args.s.replace('.sent','.txt.ol'))
	
	amrs = [x for x in open(args.d,'r')]
	sents = [s.strip() for s in open(args.s,'r')]
	
	print '# ::snt ' + sents[0]
	amr_num = 1
	for idx, line in enumerate(amrs):
		if line.strip():
			print line.rstrip()
		else:
			print ''
			try:
				print '# ::snt ' + sents[amr_num]
				amr_num += 1	
			except:
				break
