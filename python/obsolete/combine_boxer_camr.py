#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
import validator_seq2seq
import subprocess
import random

'''Combine Boxer and CAMR output'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Folder with all boxer amrs")
parser.add_argument("-c", required=True, type=str, help="Folder with CAMR amrs")
parser.add_argument("-o", required=True, type=str, help="Output-file for combined boxer + camr")
parser.add_argument("-t", required=True, type=float, help="F-score threshold")
args = parser.parse_args()


def get_boxer_dict():
	boxer_amrs = {}
	empty_amrs = 0
	idx = 0
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith('.amr'):
				idx += 1
				f_path = os.path.join(root, f)
				amr = [x.rstrip() for x in open(f_path, 'r')]
				if len(amr) > 3:
					sent = amr[2][2:]
					boxer_amrs[sent.strip()] = amr
					#print sent.strip()
				else:
					empty_amrs += 1

	print 'There were {0} empty Boxer amrs'.format(empty_amrs)
	print 'There were {0} parsed Boxer AMRs'.format(len(boxer_amrs))
	
	return boxer_amrs


def get_camr_dict():
	
	camr_amrs = {}
	
	for root, dirs, files in os.walk(args.c):
		for f in files:
			if f.endswith('.camr.amr'):
				f_path = os.path.join(root, f)
				cur_amr = []
				
				for line in open(f_path,'r'):
					if line.startswith('# ::'):
						cur_amr.append(line)
					elif not line.strip():
						sent = cur_amr[1].replace('# ::snt','').strip() 
						camr_amrs[sent] = cur_amr
						cur_amr = []      
					else:
						cur_amr.append(line)
	
	print 'Parsed {0} CAMR amrs'.format(len(camr_amrs))
	
	return camr_amrs					


def write_to_file(f, lst):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.rstrip() +'\n')
	out_f.close()		


if __name__ == '__main__':	
	
	boxer_amrs = get_boxer_dict()
	camr_amrs = get_camr_dict()
	
	found, not_found, null_edge, invalid_camr, invalid_boxer, smatch_errors, keep_count = 0,0,0,0,0,0,0
	
	f_scores = []
	
	keep_boxer = []
	
	keep_camr_4 = []
	keep_camr_5 = []
	keep_camr_6 = []
	keep_camr_7 = []
	
	rand_num = random.randint(0, 100000)		#if running multiple scripts at same time, use different temps (ugly)
	
	for idx, key in enumerate(boxer_amrs):				
		if key in camr_amrs:			
			found += 1
			c_amr = " ".join(camr_amrs[key][2:])
			b_amr = " ".join(boxer_amrs[key][3:])
			if 'null_edge' in c_amr:
				null_edge += 1
			if not validator_seq2seq.valid_amr(c_amr):
				invalid_camr += 1
			if not validator_seq2seq.valid_amr(b_amr):
				invalid_boxer += 1
		
			#if 'null_edge' not in c_amr and validator_seq2seq.valid_amr(c_amr) and validator_seq2seq.valid_amr(b_amr):
			##if 'null_edge' not in c_amr and validator_seq2seq.valid_amr(c_amr):
				#temp_camr =  'temp_camr_' + str(rand_num) + '.txt'
				#temp_boxer = 'temp_boxer_' + str(rand_num) + '.txt'
				#write_to_file(temp_camr, camr_amrs[key])
				#write_to_file(temp_boxer, boxer_amrs[key])
				#smatch_call = 'python smatch_2.0.2/smatch.py -f {0} {1}'.format(temp_camr, temp_boxer)
				
				#output = subprocess.check_output(smatch_call, shell=True)
				#f_score = output.split()[-1]
				#f_scores.append(float(f_score))
				#if float(f_score) > 0.7:
					#keep_camr_7 += camr_amrs[key]
					#keep_camr_7.append('')
				#elif float(f_score) > 0.6:
					#keep_camr_6 += camr_amrs[key]
					#keep_camr_6.append('')
				#elif float(f_score) > 0.5:
					#keep_camr_5 += camr_amrs[key]
					#keep_camr_5.append('')
				#elif float(f_score) > 0.4:
					#keep_camr_4 += camr_amrs[key]
					#keep_camr_4.append('')
	else:
		not_found += 1
	
	print '{0} found and {1} not found'.format(found, not_found)
	print 'Ignored because of null-edge: {0}'.format(null_edge)
	print 'Invalid camr: {0}'.format(invalid_camr)
	print 'Invalid boxer: {0}'.format(invalid_boxer)
	
	#print 'Smatch errors: {0}'.format(smatch_errors)
	
	#for x in range(1,10):
	#	threshold = float(x) / float(10)
	#	above = [x for x in f_scores if x > threshold]
	#	print '{0} amr-pairs with smatch score above {1}'.format(len(above), threshold)
	
	#print CAMR amrs that were saved to file
	
	#write_to_file(args.o + 'F0.7.camr.amr' , keep_camr_7)
	#write_to_file(args.o + 'F0.6.camr.amr' , keep_camr_6)
	#write_to_file(args.o + 'F0.5.camr.amr' , keep_camr_5)
	#write_to_file(args.o + 'F0.4.camr.amr' , keep_camr_4)
						
				
