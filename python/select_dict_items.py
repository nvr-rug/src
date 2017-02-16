#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re, os
import json
import argparse
import operator
from random import shuffle
import math

'''Function that reads in the dictionaries with all the permutations and distance per AMR and
   outputs desired number of permutations (random, best, worst, etc)'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Input-folder with dictionaries")
parser.add_argument('-p', required = True,type=str, help="Output folder for the AMRs + sentences")
parser.add_argument('-tp', required = True,type=str, help="Type of processing (choose random, best or best-noise)")
parser.add_argument('-num_keep', default = 5,type=int, help="Number of augmented AMRs we keep")
parser.add_argument('-pct', default = 10,type=int, help="Percentage of AMRs we check in random-noise setting")
args = parser.parse_args()

if args.tp not in ['random','best','best-noise', 'best-worst']:
	raise ValueError ('Invalid value for argument -tp')

def print_to_file(f_path, print_list):
	
	with open(f_path, 'w') as f_out:
		for line in print_list:
			f_out.write(line.strip() + '\n')
	print 'Printed {0}'.format(f_path)
	f_out.close()	


def process_dict(f_path, f_name):
	'''Process dictionary to find best items'''
	
	sents = []
	amrs = []
	
	sent_file = args.p + f_name.replace('.txt.dict','.sent')
	amr_file = args.p + f_name.replace('.txt.dict','.tf')
	
	
	with open(f_path, 'r') as f:
		d = json.load(f)	
	f.close()
	
	#avg = float(sum([len(d[k]) for k in d if len(d[k]) > 25])) / float(len([len(d[k]) for k in d if len(d[k]) > 25]))
	
	for key in d:
		old_amrs = key.split('SPLIT-HERE')[0]
		sent = key.split('SPLIT-HERE')[1]
		if len(sent) > 500: #and len(d[key]) > 100 and len(d[key]) < 200:
			d[key].sort(key=lambda x: x[1])
			print '\n\n##sent', sent
			print old_amrs,'\n'
			count = 0
			for item in d[key]:
				count += 1
				if count < 20:
					print item
		
		if args.tp == 'random':
			shuffle(d[key])							# do this for the random selection of permutations
			add_amrs = d[key][0:args.num_keep]						
		
		elif args.tp == 'best':	
			d[key].sort(key=lambda x: x[1])			# important: sort by value (distance) to select best permutations
			add_amrs = d[key][0:args.num_keep]
		
		elif args.tp == 'best-noise':
			d[key].sort(key=lambda x: x[1])
			if len(d[key]) < args.num_keep * args.pct:	# check if there are enough amrs so that we can also check different ones
				add_amrs = d[key][0:args.num_keep]	
			else:
				tmp = d[key][0:int(len(d[key]) * (float(args.pct) / 100))]		# select top X percent of AMRs
				shuffle(tmp)									# and then randomize it
				add_amrs = tmp[0:args.num_keep]	
			
		elif args.tp == 'best-worst':						# best-worst is also selected in top X%
			
			best_amrs = sorted(d[key], key = lambda x: x[1])
			worst_amrs = sorted(d[key], key = lambda x: x[1], reverse = True)
			
			best_amrs = best_amrs[0:args.num_keep * args.pct]
			worst_amrs = worst_amrs[0:args.num_keep * args.pct]

			shuffle(best_amrs)				# after selecting top X%, shuffle them
			shuffle(worst_amrs)
			
			add_amrs = best_amrs[0:int(math.ceil(float(args.num_keep) / 2.0))] + worst_amrs[0:int(math.ceil(float(args.num_keep) / 2.0))]						
		
		for item in add_amrs:
			if item[0] not in amrs:
				amrs.append(item[0])
				sents.append(sent)
	
	print '{2} Old: {0} New: {1}'.format(len(d), len(amrs), f_path.split('/')[-1])
	
	#print_to_file(sent_file, sents)
	#print_to_file(amr_file, amrs)			
	
	return amrs, sents

if __name__ == "__main__":
	all_amrs = []
	all_sents = []
	
	for root, dirs, files in os.walk(args.f):
		for f in files:
			f_path = os.path.join(root, f)
			amrs, sents = process_dict(f_path, f)
			all_amrs += amrs
			all_sents += sents
	
	#name_amrs  = args.p + 'deft-p2-amr-r2-amrs-training-all.sent'
	#name_sents = args.p + 'deft-p2-amr-r2-amrs-training-all.tf'	
	
	#print_to_file(name_amrs, all_amrs)
	#print_to_file(name_sents, all_sents)
