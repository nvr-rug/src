#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
import utils, subprocess
from multiprocessing import Pool

'''Script for running CAMR preprocessing in parallel'''

parser = argparse.ArgumentParser()
parser.add_argument("-c", required=True, type=str, help="Starting directory CAMR output")
parser.add_argument("-j", required=True, type=str, help="Starting directory JAMR output")
parser.add_argument("-extc", default = '.camr.amr', type=str, help="Extension of parsed CAMR files")
parser.add_argument("-extj", default = '.jamr.amr', type=str, help="Extension of parsed JAMR files")
parser.add_argument("-d", required = True, type=str, help="Where to save the dictionaries")
parser.add_argument("-max_threads", default = 8, type=int, help="Max number of parallel threads")
args = parser.parse_args()


#def put_in_one_line(f):

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def save_log(f):
	with open(f,'w') as out_f:
		out_f.write('Done {0}\n'.format(f))
	out_f.close()	


def remove_log(f):
	os.system('rm {0}'.format(f)) 


def process_sentences(camr_file, jamr_file, log_dir, raw_j):
	sentence_camr_file = camr_file + '.sent'
	sentence_jamr_file = jamr_file + '.sent'
	
	os.system('grep "# ::snt" {0} > {1}'.format(camr_file, sentence_camr_file))
	os.system('grep "# ::snt" {0} > {1}'.format(jamr_file, sentence_jamr_file))
	
	sent_camr = [x for x in open(sentence_camr_file,'r')]
	sent_jamr = [x for x in open(sentence_jamr_file,'r')]
	
	if len(sent_camr) == len(sent_jamr) and len(sent_jamr) != 0:
		return [sentence_camr_file, sentence_jamr_file]
	else:
		print 'Sentences not of equal length for {0} and {1}, len {2} vs len {3}'.format(sentence_camr_file, sentence_jamr_file, len(sent_camr), len(sent_jamr))	
		print 'Remove log-file, just keep trying, maybe JAMR was still parsing\n'
		remove_log(log_dir + raw_j)
		return []


def one_line_process(camr_file, jamr_file, log_dir, raw_j):
	os.system('python camr_one_line.py -f {0} -out_ext .ol'.format(camr_file))
	os.system('python camr_one_line.py -f {0} -out_ext .ol'.format(jamr_file))
	
	camr_ol = camr_file + '.ol'
	jamr_ol = jamr_file + '.ol'
	
	len_camr_ol = len([x for x in open(camr_ol,'r')])
	len_jamr_ol = len([x for x in open(jamr_ol,'r')])
	
	if len_camr_ol == len_jamr_ol and len_camr_ol != 0:
		return [camr_ol, jamr_ol]
	else:
		print 'One-line AMR files are of different length for {0} and {1}, len {2} vs {3}'.format(camr_ol, jamr_ol, len_camr_ol, len_jamr_ol)	
		#print 'Remove log and keep trying'
		#remove_log(log_dir + raw_j)
		return []


def create_smatch_dict(camr_ol, jamr_ol, camr_sent, dict_file):
	os_call = 'python compare_two_AMR_files.py -f1 {0} -f2 {1} -sent {2} -d {3}'.format(camr_ol, jamr_ol, camr_sent, dict_file)
	os.system(os_call)	


def process_file(arg_list):
	camr_file = arg_list[0]
	jamr_file = arg_list[1]
	dict_loc = arg_list[2]
	log_dir = arg_list[3]
	raw_j = arg_list[4]
	
	sentence_files = process_sentences(camr_file, jamr_file, log_dir, raw_j)
	one_line_files = one_line_process(camr_file, jamr_file, log_dir, raw_j)			
	
	if sentence_files and one_line_files:											#no errors found in sentences and one-line files
		dict_file = dict_loc + raw_j + '.dict'
		create_smatch_dict(one_line_files[0], one_line_files[1], sentence_files[0], dict_file)	#create smatch dictionary
	
			
if __name__ == '__main__':
	processed_files = []
	log_dir = args.d + 'already_done/'
	
	check_list = []
	for root_c, dirs_c, files_c in os.walk(args.c):
		for f_c in files_c:
			raw_c = f_c.replace(args.extc,'')
			for root_j, dirs_j, files_j in os.walk(args.j):
				for f_j in files_j:  
					raw_j = f_j.replace(args.extj,'')
					if f_c.endswith(args.extc) and f_j.endswith(args.extj) and raw_j == raw_c and is_non_zero_file(os.path.join(root_c, f_c)) and is_non_zero_file(os.path.join(root_j, f_j)) and not os.path.isfile(log_dir + raw_j):			#matching files for processing			
						check_list.append([os.path.join(root_c, f_c), os.path.join(root_j,f_j), args.d, log_dir, raw_j])
		
	max_processes = min(args.max_threads, len(check_list))
	print len(check_list)	
	if max_processes > 0:
		print 'Testing {0} files, {1} in parallel'.format(len(check_list), max_processes)
		pool = Pool(processes=max_processes)						
		pool.map(process_file, check_list)						# test directories in parallel
