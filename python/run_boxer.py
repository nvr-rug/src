#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
import subprocess
from multiprocessing import Pool

'''Tokenize, parse and then run Boxer on sentences'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File with to be parsed sentences")
parser.add_argument("-fol", required=True, type=str, help="Folder to save individual sentences with their parse/tokenization")
args = parser.parse_args()

# RUN THIS FIRST: export PATH=/net/gsb/gsb/ext/elephant:/net/gsb/gsb/ext/elephant/ext:$PATH


def boxer(f):
	os.system('/net/gsb/gsb/ext/candc/bin/boxer --input {0} --semantics amr --copula false --modal --elimeq --theory sdrt --warnings --integrate > {0}.amr'.format(f))

def parse(f):
	#run C&C parser
	os.system("""/net/gsb/gsb/ext/candc/bin/candc --input {0} --models /net/gsb/gsb/ext/candc/models/boxer --candc-printer boxer --candc-int-betas "0.075 0.03 0.01 0.005 0.001 0.0001 0.00001 0.00001" --candc-int-dict_cutoffs "20 20 20 20 150 150 150 200" --candc-parser-maxsupercats 1000000 > {0}.ccg""".format(f))


def tokenize(f):
	
	os.system(u'cat {0} | /net/gsb/gsb/ext/elephant/elephant -m /net/gsb/gsb/ext/elephant/models/english -f iob | sed -e "s/\t/ /" > {0}.tok.iob'.format(f))
	
	# convert to tokenization pivot format (used by various tools to map tokens to offsets etc.)
	os.system('cat {0}.tok.iob | /net/gsb/gsb/src/python/iob2off.py > {0}.tok.off'.format(f))
	
	# convert to tokenization format used by POS tagger
	os.system('cat {0}.tok.off | /net/gsb/gsb/src/python/off2tok.py > {0}.tok'.format(f))

	# HACK: straighten quotes (not all tools deal with typographical ones)
	os.system("""cat {0}.tok | sed -e "s/[‘’]/'/g" | sed -e 's/[“”]/"/g' > {0}.tok.normalized""".format(f))

def process_file(f_path):
	
	print 'Start testing file {0}'.format(f_path)
	
	for idx, line in enumerate(open(f_path,'r')):
		
		line_num = 'part' + f_path.split('_')[-1].split('.')[0] + '_' + str(idx)
		
		if os.path.isfile(args.fol + 'sent_' + str(line_num) + '.tok'):
			raise ValueError("File exists already, should never happen")
		else:
			with open(args.fol + 'sent_' + str(line_num) + '.tok','w') as tmp:
				tmp.write(line.strip() + '\n')
			tmp.close()	
		
		#tokenize(args.fol + 'sent_' + str(idx+1) + '.txt')
		parse(args.fol + 'sent_' + str(line_num) + '.tok')
		boxer(args.fol + 'sent_' + str(line_num) + '.tok.ccg')

if __name__ == '__main__':		
	
	#files = os.listdir(args.f)
	for root, dirs, files in os.walk(args.f):
		do_files = [os.path.join(root, f) for f in files if f.endswith('.filtered')]
	
	pool = Pool(processes=24)						
	pool.map(process_file, do_files)
			
	
	
