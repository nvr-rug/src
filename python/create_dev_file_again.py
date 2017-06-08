#!/usr/bin/env python

import os
import re
import sys
import subprocess
import argparse
import random
import json
from multiprocessing import Pool
import datetime
from Levenshtein import jaro

'''Script that produces the Smatch output for CAMR, Boxer and Seq2seq produced AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument('-g', required=True, type=str, help="Folder with gold AMR files")
parser.add_argument('-d', required = True, type=str, help="dev folder")
args = parser.parse_args()


def fix_chars(f):
	sents = [x.strip().lower() for x in open(f, 'r')]
	new_sents = []
	
	for s in sents:
		new_s = s.replace(' ','').replace('+',' ')
		new_sents.append(new_s)
	
	return new_sents	


def fix_pos(f):
	sents = [x.strip().lower() for x in open(f, 'r')]
	new_sents = []
	
	for s in sents:
		new_s = " ".join([x.split('|')[0] for x in s.split()])
		new_sents.append(new_s)
	
	return new_sents	


def fix_char_pos(f):
	sents = [x.strip().lower() for x in open(f, 'r')]
	new_sents = []
	
	for s in sents:
		new_s = "".join([x for x in s.split() if len(x) == 1]).replace('+',' ')
		new_sents.append(new_s)
	
	return new_sents	
		
		
		
def create_dev_gold(dev_gold, dev_folder, order):
	gold_lines = []
	files_found = 0
	for o in order:
		for root, dirs, files in os.walk(dev_gold):
			for f in files:
				if f.endswith('.txt') and o in f:
					lines = [x for x in open(os.path.join(root, f),'r')]
					gold_lines += lines
					files_found += 1
	
	sents = [x.replace('# ::snt ','').replace('# ::tok ','').strip() for x in gold_lines if x.startswith('# ::snt') or x.startswith('# ::tok')]
	print 'Found {0} sents'.format(len(sents))
	
	print '{0} files found to append'.format(files_found)
	
	out_file_txt = dev_folder + 'created_dev.txt.gold'
	out_file_sent = dev_folder + 'created_dev.sent.gold'
	
	with open(out_file_txt,'w') as out_f:
		for l in gold_lines:
			out_f.write(l.rstrip() + '\n')
	out_f.close()						
	
	with open(out_file_sent,'w') as out_f:
		for l in sents:
			out_f.write(l.strip() + '\n')
	out_f.close()				
					

def get_order(sents, gold_dict):
	order = []
	check_line_num = 0
	while len(order) < len(gold_dict):
		line_check = sents[check_line_num]
		best_sim = [0, 'none_found']
		for key in gold_dict:
			check_sent = gold_dict[key][0]
			similarity = jaro (line_check, check_sent)
			#print similarity
			if similarity > best_sim[0]:
				best_sim = [similarity, key, line_check, check_sent]
					
		if best_sim[1] == 'none_found':
			print 'This should never happen (none_found)'
		elif best_sim[1] in order:
			print 'This should never happen (already found)'
			print best_sim[1]
		else:
			print 'Found {0} as most likely, similarity {1}'.format(best_sim[1], best_sim[0])
			#print best_sim[2]
			#print best_sim[3],'\n'
			order.append(best_sim[1])
			check_line_num += len(gold_dict[best_sim[1]])
	
	print 'Final order: {0}'.format(order)
	print 'Number of lines:', check_line_num			
	
	return order					

def create_gold_file():
	print 'Re-creating dev-file because alignment might be wrong..\n'
	dev_gold = args.g.replace('dev_all','dev')
	gold_dict = {}
	for root, dirs, files in os.walk(dev_gold):
		for f in files:
			if f.endswith('.sent'):
				ident = f.split('-')[6].split('.')[0]
				sents = [x.strip().lower() for x in open(os.path.join(root, f), 'r')]
				gold_dict[ident] = sents
	
	dev_folder = args.d
	
	sents = [x for x in os.listdir(dev_folder) if x.endswith('.sent') and '.pos.sent' not in x and '.char.sent' not in x]
	char_sents = [x for x in os.listdir(dev_folder) if x.endswith('.char.sent') and '.pos' not in x ]
	pos_sents = [x for x in os.listdir(dev_folder) if x.endswith('.sent.pos') and '.char' not in x ]
	char_pos_sents = [x for x in os.listdir(dev_folder) if x.endswith('.sent.pos')]
	
	if sents:
		s = [x.strip().lower() for x in open(dev_folder + sents[0],'r')]
		print 'Found sent file'
	elif char_sents:
		s = fix_chars(dev_folder + char_sents[0])
		print 'Found char-file'
	elif pos_sents:
		s = fix_pos(dev_folder + pos_sents[0])
		print 'Found POS file'
	elif char_pos_sents:
		s = fix_char_pos(dev_folder + char_pos_sents[0])
		print 'Found char-POS file'
	else:
		print 'No suitable dev file found, exiting'
		sys.exit(0)
	
	order = get_order(s, gold_dict)	
	create_dev_gold(dev_gold, dev_folder, order)

if __name__ == '__main__':
	create_gold_file()
