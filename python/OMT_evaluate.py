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
parser.add_argument('-eval_folder', required = True, type=str, help="Evaluation folder")
parser.add_argument('-exp_name', required = True, type=str, help="Name of experiment")
parser.add_argument('-mx', required=False, type=int, default = 4, help="Number of maxthreads")
parser.add_argument('-rs', required=False, type=int, default = 4, help="Number of restarts for smatch")
parser.add_argument('-train_size', required=False, type=int, default = 33248 , help="Train size")
parser.add_argument('-range_sen', nargs='+', type=int, default = [], help ='Range of sentence length [min max]')
parser.add_argument('-range_words', nargs='+', type=int, default = [], help ='Set range of words instead of chars [min max]')
parser.add_argument('-roots_to_check', required = True, help = 'Root folder to check for output results')
parser.add_argument('-prod_ext', default = '.seq.amr.restore', type=str, help="Ext of produced files")
parser.add_argument('-gold_ext', default = '.txt', type=str, help="Ext of produced files")
parser.add_argument('-check', required = True, type=str, help="Include check-files or not")
parser.add_argument('-to_process', required = True, type=str, help="Include check-files or not")
parser.add_argument('-num_gold_files', default = 5, type=int, help="Number of individual gold files (5 for LDC2)")

args = parser.parse_args()


def do_args_check():
	if args.to_process == 'dev':
		res_dict_file = args.eval_folder + 'res_dict_dev.txt'
		gold_root = args.g.replace('/test','/dev_all')
	elif args.to_process == 'test':
		res_dict_file = args.eval_folder + 'res_dict.txt'
		gold_root = args.g
	else:	
		print '-to_process must be dev or test'
		sys.exit(0)
	
	if args.check == 'rest':
		#ids = ['.seq.amr.restore', '.seq.amr.restore.pruned','seq.amr.restore.check']
		ids = ['.seq.amr.restore']
		print 'Use new IDs'
	elif args.check == 'all':
		ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.coref', '.seq.amr.restore.pruned','seq.amr.restore.check','.seq.amr.restore.check.pruned.wiki.coref.all']
	elif args.check == 'old':
		print 'Use old IDs'
		ids = ['.seq.amr.restore','.seq.amr.restore.wiki', '.seq.amr.restore.coref', '.seq.amr.restore.pruned','.seq.amr.restore.pruned.wiki.coref.all']
	elif args.check == 'coref':
		ids = ['.seq.amr.restore.coref', '.seq.amr.restore.corefrandom', '.seq.amr.restore.corefdelete', '.seq.amr.restore.corefclosest']
	else:
		print '-check should be rest, all or old, exiting...'
		sys.exit(0)
	return ids, res_dict_file, gold_root

def combined_output_smatch(prod_ext, one_line, prod_dir, gold_root):
	'''Combine the tested files to obtain an average F1-score'''
	
	total_gold = []
	total_prod = []
	res = False
	added = 0
	
	order = []
	
	for root1, dirs1, files1 in os.walk(prod_dir):
		for f1 in files1:
			for root2, dirs2, files2 in os.walk(args.g):
				for f2 in files2:
					if f1.endswith(prod_ext) and f2.endswith(args.gold_ext):
						res = True
						match_p = f1.split('-')[-1].split('.')[0]
						match_g = f2.split('-')[-1].split('.')[0]
						match_part_p = f1.replace(match_p,'average')
						match_part_g = f2.replace(match_g,'average')
						if match_p == match_g:
							order.append(match_p)
							prod_amrs = [x.rstrip() for x in open(os.path.join(root1, f1))]
							gold_amrs = [x.rstrip() for x in open(os.path.join(root2, f2))]
							total_prod += prod_amrs
							total_gold += gold_amrs	
							added += 1
	
	if res and added == args.num_gold_files:			#check if we found result and also the correct number of files for the result
		prod_file = prod_dir + '/' + match_part_p

		print 'Order for', prod_dir.split('/')[-1], prod_ext
		print order,'\n'
		
		uniq_id = random.randint(0, 10000)
		gold_file = gold_root + match_part_g + '_' + str(uniq_id)
		
		with open(prod_file,'w') as out_f:
			for p in total_prod:
				out_f.write(p.strip() + '\n')
		out_f.close()			
		
		with open(gold_file,'w') as out_f:
			for g in total_gold:
				out_f.write(g.rstrip() + '\n')
		out_f.close()
		
		os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r {3} {2} -f {0} {1}'.format(prod_file, gold_file, one_line, 30) #change 30 back to args.rs if necessary
		f_score, num_sen = do_smatch(os_call, False)
		
		os.system('rm {0}'.format(gold_file))	#remove gold file again
		#print 'F-combined {0}'.format(f_score)
		return f_score, num_sen, res
	else:
		return 0, 0, False	
			
def prepare_data(ids, dict_file, gold_root):
	dirs_to_check = os.walk(args.roots_to_check).next()[1]
	
	model_type = []
	all_epochs = []
	for fol in dirs_to_check:
		for idx, ident in enumerate(ids):
			if 'epoch' not in fol:
				train_inst = fol.split('-')[-1]
				ep_num = round(float(train_inst) / float(args.train_size),1)
				all_epochs.append(ep_num)
			else:
				ep_num = float(re.findall(r'epoch([\d]+)', fol)[0])
				all_epochs.append(ep_num)
	
			idf = ident.split('.')[-1]
			m_type = '{0} epochs ({1}) '.format(ep_num, idf)		
			model_type.append(m_type)
		
	gold_ids, gold_files = get_gold_ids(gold_root)
	
	#don't do smatch way too many times; store results in dict, try to read them here
	
	if os.path.isfile(dict_file):
		with open(dict_file, 'r') as in_f:
			res_dict = json.load(in_f)
		in_f.close()
		print 'Read in dict with len {0}'.format(len(res_dict))
		for idn in model_type:
			if idn not in res_dict:
				res_dict[idn] = []
	else:	
		res_dict = create_res_dict(model_type)
		print 'Started testing from scratch'	
	
	return model_type, gold_ids, gold_files, res_dict, dirs_to_check, all_epochs	


def get_gold_ids(root):
	gold_ids = []
	gold_files = []
	for r, d, files in os.walk(root):
		for f in files:
			if '.txt' in f:
				if args.to_process == 'dev':
					gold_ids.append('dev')
				else:
					gold_ids.append(f.split('-')[6].split('.')[0])
				gold_files.append(f)
	return gold_ids, gold_files		


def create_res_dict(gold_ids):
	res_dict = {}
	for idn in gold_ids:
		res_dict[idn] = []
	
	return res_dict	


def get_gold_file(ident, gold_files):
	for f in gold_files:
		if ident in f:
			return f
	
	raise ValueError('No matching file found')		


def do_smatch(os_call, range_check):
	'''Runs the smatch OS call'''
	
	output = subprocess.check_output(os_call, shell=True)
	f_score = output.split()[-1]		# get F-score from output
	num_sen = output.split()[-4]
	
	if range_check:
		skipped_sen = output.split()[-7]
		processed_sen = int(total_sen) - int(skipped_sen)
		print 'Skipped sentences for {0} : {1} out of {4} (range {2}-{3})'.format(f.split('-')[-1].replace('.txt',''), skipped_sen, args.range_words[0], args.range_words[1], total_sen)
		return f_score, processed_sen
	else:	
		return f_score, num_sen
			

def evaluate(entry, ident, model, gold_ids, gold_files, res_dict, gold_root):
	'''Will print smatch scores for Seq2seq checkpoints'''

	one_line = '--one_line'
	
	if args.to_process == 'test':
		f_score, num_sen, res = combined_output_smatch(ident, one_line, entry, gold_root)	#calculate combination first
		if res:
			res_dict[model].append(['average', f_score, int(num_sen)])
		else:
			print 'No results for folder {0} and ident {1}'.format(entry, ident)	
	
	for root, dirs, files in os.walk(entry):
		for f in files:
			if f!= [] and f.endswith(ident) and 'average' not in f:			# sometimes rubbish files in there, only find the file with the produced AMR
				for idn in gold_ids:					# check if it matches with a file in the gold map
					if idn in f:
						produced_f = os.path.join(root,f)
						if os.path.getsize(produced_f) > 0:
							if args.to_process == 'test':
								gold_f = os.path.join(gold_root, get_gold_file(idn, gold_files))
							else:
								gold_f = args.eval_folder.replace('/evaluation','/working/dev') + 'created_dev.txt.gold'
								if not os.path.isfile(gold_f):
									print 'Gold file doesnt exists, maybe run create_dev_file_again.py, now exiting...'
									sys.exit(0)
								
							if not args.range_sen and not args.range_words: # the normal output
								os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r {3} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.rs)
								f_score, num_sen = do_smatch(os_call, False)
								res_dict[model].append([idn, f_score, int(num_sen)])
								print 'F-score {0} for model {1} and ident {2} and idn {3}'.format(f_score, model, ident, idn)
							
							elif args.range_words and not args.range_sen:		#only calculate smatch for sentences with certain word range
								os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch_max_length.py -w1 {3} -w2 {4} -r {5} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.range_words[0], args.range_words[1], args.rs)	
								f_score, processed_sen = do_smatch(os_call, True)
								res_dict[model].append([idn, f_score, processed_sen])
							
							elif args.range_sen and not args.range_words:			# only calculate smatch score for sentences within a certain character range
								os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch_max_length.py -b1 {3} -b2 {4} -r {5} {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.range_sen[0], args.range_sen[1], args.rs)	
								f_score, processed_sen = do_smatch(os_call, True)
								res_dict[model].append([idn, f_score, processed_sen])
							else:
								raise ValueError("Don't do both range_sen and range_words")
						elif 'wiki' not in produced_f:
							print produced_f			
		break				
	return res_dict					
		
						
def fix_res_list(all_res):
	return_res = []
	for idx in range(len(all_res[0])):
		return_res.append("\t".join(all_res[0][idx]) + '\t' +  "\t".join(all_res[1][idx]))
	
	return return_res	

def add_average(d):
	for key in d:
		total_f, total_sen, did_item = 0, 0, False
		for item in d[key]:
			did_item = True
			total_sen += item[2]
			total_f += float(item[2]) * float(item[1])
		if did_item:
			avg_f = round(float(total_f) / float(total_sen),5)
			d[key].append(['avg',str(avg_f),str(total_sen)])
		else:
			d[key].append(['avg','',''])	
	
	return d	

def print_nice_output(res_dict, gold_ids, model_type, all_epochs):
	'''Print nice output to terminal and evaluation file'''
	
	if 'average' not in gold_ids and args.to_process == 'test':
		gold_ids.append('average')		#add for average
	gold_ids = list(set(gold_ids))
	
	print '\nResults for', args.to_process,  args.exp_name +':\n'
	print '\n\t\t\t\t' + "\t".join(gold_ids).replace('consensus','consen')  # last replace for nicer printing
	res_list = [[],[],[]]
	
	#res_dict = add_average(res_dict)
	
	print_list = []
	for m in model_type:
		num_tabs = int(((8*4) - len(m)) / 8) 
		print_l = m + num_tabs * '\t'
		for idn in gold_ids:					## test file options
			for key in res_dict:
				if key == m:					## we have the right model
					for item in res_dict[key]:
						if item[0] == idn:		## get right file
							print_l += '\t' + str(item[1])
		print_list.append(print_l)					
	
	printer = [y[1] for y in sorted([[float(z.split()[0]), z] for z in print_list], key = lambda x : x[0])] #sort by number of epochs
	for p in printer: print p
	
	eval_file = args.eval_folder + args.to_process.upper() + '_eval_' + str(int(round(max(all_epochs),0))) + 'eps' + datetime.datetime.now().strftime ("_%d_%m_%Y_") +  '.txt'
	
	
	with open(eval_file, 'w') as out_f:
		out_f.write('Results for ' + args.exp_name + ':\n\n')
		for p in printer:
			out_f.write(p.strip() + '\n')
	out_f.close()		
	
	return res_list
	
		
if __name__ == '__main__':
	
	ids, res_dict_file, gold_root = do_args_check()
	model_type, gold_ids, gold_files, res_dict, dirs_to_check, all_epochs = prepare_data(ids, res_dict_file, gold_root)
	
	counter = 0
	
	print 'Testing {0} dirs\n'.format(len(dirs_to_check))
	
	for idx, root in enumerate(dirs_to_check):
		for ident in ids:
			root_fix = args.roots_to_check + root
			if res_dict[model_type[counter]] == []:
				res_dict = evaluate(root_fix, ident, model_type[counter], gold_ids, gold_files, res_dict, gold_root)
			
			counter += 1
	
	res_list = print_nice_output(res_dict, gold_ids, model_type, all_epochs)
	
	#save smatch results to dict
	
	with open(res_dict_file, 'w') as out_f:
		json.dump(res_dict, out_f)
	out_f.close()	
		
