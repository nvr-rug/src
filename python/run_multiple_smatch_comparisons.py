#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
import utils, subprocess
from multiprocessing import Pool

'''Script for running CAMR preprocessing in parallel'''

parser = argparse.ArgumentParser()
parser.add_argument("-c", required=True, type=str, help="Starting directory CAMR output")
parser.add_argument("-j", required=True, type=str, help="Starting directory JAMR output")
parser.add_argument("-extc", default = '.camr.amr.ol', type=str, help="Extension of parsed CAMR files")
parser.add_argument("-extj", default = '.jamr.amr.ol', type=str, help="Extension of parsed JAMR files")
parser.add_argument("-d", required = True, type=str, help="Where to save the dictionaries")
parser.add_argument("-max_threads", default = 12, type=int, help="Max number of parallel threads")
args = parser.parse_args()


def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def create_smatch_dict(camr_ol, jamr_ol, camr_sent, dict_file):
	os_call = 'python compare_two_AMR_files.py -f1 {0} -f2 {1} -sent {2} -d {3}'.format(camr_ol, jamr_ol, camr_sent, dict_file)
	#print os_call
	os.system(os_call)	


def process_file(arg_list):
	camr_file = arg_list[0]
	jamr_file = arg_list[1]
	dict_loc = arg_list[2]
	raw_j = arg_list[3]
	sent_file = camr_file.replace('.ol','.sent')
	
	if not os.path.isfile(sent_file):
		print '{0} is not a file'.format(sent_file)
	else:	
		dict_file = dict_loc + raw_j + '.dict'
		create_smatch_dict(camr_file, jamr_file, sent_file, dict_file)	#create smatch dictionary
	
			
if __name__ == '__main__':
	processed_files = []
	
	check_list = []
	for root_c, dirs_c, files_c in os.walk(args.c):
		for f_c in files_c:
			raw_c = f_c.replace(args.extc,'')
			for root_j, dirs_j, files_j in os.walk(args.j):
				for f_j in files_j:  
					raw_j = f_j.replace(args.extj,'')
					if f_c.endswith(args.extc) and f_j.endswith(args.extj) and raw_j == raw_c and is_non_zero_file(os.path.join(root_c, f_c)) and is_non_zero_file(os.path.join(root_j, f_j)):			#matching files for processing			
						check_list.append([os.path.join(root_c, f_c), os.path.join(root_j,f_j), args.d, raw_j])
		
	max_processes = min(args.max_threads, len(check_list))	
	if max_processes > 0:
		print 'Testing {0} files, {1} in parallel'.format(len(check_list), max_processes)
		pool = Pool(processes=max_processes)						
		pool.map(process_file, check_list)						# test directories in parallel
