#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that tokenizes the sentences in the rawdata'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains the amrs")
parser.add_argument('-tf', required = True, help="output directory for output-files")
parser.add_argument('-extension', required = False, default = '.txt', help="extension of AMR files (default .txt)")
parser.add_argument('-temp_dir', required = True, help="Temp directory for the elephant files")
args = parser.parse_args()

def tokenize(line):		
	system_line = line.replace('# ::snt ','').strip()
	
	os.system('echo "' + system_line + '" | /net/gsb/gsb/ext/elephant/elephant -m /net/gsb/gsb/ext/elephant/models/english/ -f iob | sed -e "s/\t/ /" > {0}temp.tok.iob'.format(args.temp_dir))
	os.system('cat {0}temp.tok.iob | ~/Documents/pmb_lc/src/python/iob2off.py > {0}temp.tok.off'.format(args.temp_dir))
	os.system('cat {0}temp.tok.off | /net/gsb/pmb/src/python/off2tok.py > {0}temp.tok.raw'.format(args.temp_dir))
	os.system("""cat {0}temp.tok.raw | sed -e "s/[‘’]/'/g" | sed -e 's/[“”]/"/g' > {0}temp.tok""".format(args.temp_dir))	# straighten out quotes for sentence
	
	tokenized =  " ".join([x.strip() for x in open('{0}temp.tok'.format(args.temp_dir),'r')])
	
	return tokenized
		

def process_file(f, out_f):
	all_lines = []
	error_processing = 0
	for idx ,line in enumerate(open(f, 'r')):
		#if idx % 1000 == 0:
		#	print 'idx:',idx, ' errors:', error_processing,'\n'
		
		if line.startswith('# ::snt'):
			
			tokenized_line = tokenize(line)
			
			if tokenized_line == '':
				print 'Tokenization failed!'
				error_processing += 1
				all_lines.append(line)
			else:
				all_lines.append('# ::snt ' + tokenized_line)
		else:	
			all_lines.append(line)	
	
	with open(out_f, 'w') as f_out:
		for line in all_lines:
			f_out.write(line.replace('\n','') +'\n')
	f_out.close()
	
	os.system("""cat {0} | sed -e "s/[‘’]/'/g" | sed -e 's/[“”]/"/g' > {1}""".format(out_f, out_f.replace(args.extension,'.norm' + args.extension))) # straighten out quotes for file		
	
	print 'Errors in {0}: {1}'.format(f, error_processing)
	
	return error_processing				
			

if __name__ == '__main__':
	total_errors = 0
	
	os.system('export PATH=/net/gsb/gsb/ext/elephant:/net/gsb/gsb/ext/elephant/ext:$PATH')
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.extension):
				print f
				f_path = os.path.join(root, f)
				out_f = args.tf + f
				errors = process_file(f_path, out_f)
				total_errors += errors
	print 'Total errors over all files:',total_errors
	


#try:
	#line = "".join(c.upper() if idx == 0 else c for idx, c in enumerate(line.replace('# ::snt ','').strip()))			#sometimes something goes wrong in Elephant with lowercase first letters, just capitalize it then
	#tokenized_line = tokenize(line)
	
	#if tokenized_line == '':
		#print 'Try again failed due to error in tokenizer'
		#error_processing += 1
		#all_lines.append(line)
	#else:
		#print 'Try again succeeded'
		#all_lines.append('# ::snt ' + tokenized_line)	
	#except:	
		#print 'Try again failed due to error in try/except'
		#all_lines.append(line)
		#error_processing += 1				
