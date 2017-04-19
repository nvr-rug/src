#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Script that changes the UKWAC format to sentences'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Folder with UKWAC XML files")
parser.add_argument("-o", required=True, type=str, help="Output file")
parser.add_argument("-ext", default='.xml', type=str, help="Extension of UKWAC XML files")
args = parser.parse_args()


def get_num_words(line):
	num_words =0
	for w in line.split():
		if len(w) > 1 or w.isalpha() or w.isdigit():
			num_words += 1
	
	return num_words

def filter_line(line):
	'''Filter lines found in corpus, no weird character of strange quotes'''
	
	line = line.replace('“','"').replace('”','"').replace('`',"'")
	line = " ".join(line.split()) #remove double spaces
	new_data = []
	
	filter_chars = [']','[','}','{','_','>','<', '|','~','+','&','---']
	
	if not any(x in line for x in filter_chars):			#filter sentences with those characters, too often weird
		if line and (line[0].isalpha() or line[0] == '"'):
			if len(line.split()) > 4 and get_num_words(line) > 3 and line.count('"') % 2 == 0:	#only include sentences with correct number of quotes that are long enough
				return line
	
	return ''	


def process_file(f):
	cur_sent = []
	all_sents = []
	for line in open(f,'r'):
		if line.strip() == '<s>':		#start new sentence
			cur_sent = []
		elif line.strip() == '</s>':		#finished sentence, save results
			sent = filter_line(" ".join(cur_sent))
			if sent:
				all_sents.append(sent)
			cur_sent = []
		else:
			word = line.split()[0].strip()
			cur_sent.append(word)
	
	return all_sents			

if __name__ == "__main__":
	all_sents = []
	
	for root, dirs,files in os.walk(args.f):
		for f in files:
			if f.endswith(args.ext):
				file_sents = process_file(os.path.join(root, f))
				all_sents += file_sents
	
	with open(args.o, 'w') as out_f:
		for a in all_sents:
			out_f.write(a.strip() + '\n')
	out_f.close()					
