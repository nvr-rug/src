#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

'''Script that filters corpus sentences that we do not want'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File with fill corpus")
parser.add_argument("-o", required=True, type=str, help="Output file")
parser.add_argument("-t", default ='', type=str, help="Do tokenization?")
args = parser.parse_args()


def get_num_words(line):
	num_words =0
	for w in line.split():
		if len(w) > 1 or w.isalpha() or w.isdigit():
			num_words += 1
	
	return num_words

def filter_line(line):
	'''Filter lines found in corpus, no weird character or strange quotes'''
	
	line = line.replace('“','"').replace('”','"').replace('`',"'")
	line = " ".join(line.split()) #remove double spaces
	new_data = []
	
	filter_chars = [']','[','}','{','_','>','<', '|','~','+','&','---']
	if len(line) > 1 and line[0].isalpha() and line[0].isupper() and line[1].isalpha() and line[1].islower():
		if not any(x in line for x in filter_chars):			#filter sentences with those characters, too often weird
			if len(line.split()) > 4 and get_num_words(line) > 3: 
				if line.count('"') % 2 == 0:	#only include sentences with correct number of quotes that are long enough
					return line
					
	return ''	


def check_utf8(line):
	valid_utf8 = True
	try:
		line.decode('utf-8')
	except UnicodeDecodeError:
		valid_utf8 = False
	
	return valid_utf8


if __name__ == "__main__":
	all_sents = []
	
	for idx, line in enumerate(open(args.f,'r')):
		if idx % 100000 == 0:
			print idx, len(all_sents)
		
		if args.t:
			tok_line = " ".join(nltk.word_tokenize(line))
		else:
			tok_line = line
		
		if check_utf8(tok_line):
			new_l = filter_line(tok_line)
			if new_l:
				all_sents.append(new_l)
	
	
	
	with open(args.o, 'w') as out_f:
		for a in all_sents:
			out_f.write(a.strip() + '\n')
	out_f.close()					
