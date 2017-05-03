#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script create AMR-files based om smatch scores from dictionary
   input: d[sent] = [CAMR, JAMR, f-score]'''

import re,sys, argparse, os, subprocess, json
from random import shuffle
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-d", required = True, type=str, help="Dictionary folder with smatch results")
parser.add_argument("-dic", default = '', type=str, help="Full dict file, if empty we create it")
parser.add_argument("-f1", required = True, type=str, help="Folder to save AMR files with AMRs per F-score")
parser.add_argument("-f2", default = '', type=str, help="Folder to save AMR files by F-score with fixed number of AMRs")
parser.add_argument("-f3", default = '', type=str, help="Folder to save AMR files with F-score random and # of AMRs constant")
args = parser.parse_args()

def write_to_file(lst, f):
	x = 1
	#with open(f, 'w') as out_f:
	#	for l in lst:
	#		out_f.write(l.strip() + '\n')
	#out_f.close()		

def get_avg_sen_len(sents):
	total_len = 0
	for sent in sents:
		spl_sen = sent.split()
		for s in spl_sen:
			if len(s) > 1:
				total_len += 1
			elif s.isdigit() or s.isalpha():
				total_len += 1		
	
	avg_length = float(total_len) / float(len(sents))
	return avg_length

def check_errors(res):
	sents = []
	camr = []
	jamr = []
	f_scores = []
	
	for key in res:
		sents.append(key)
		camr.append(res[key][0])
		jamr.append(res[key][1])
		f_scores.append(res[key][2])
	
	new_sents = []
	new_jamr = []
	new_camr = []
	new_f_scores = []
	
	with open('temp.txt', 'w') as out_f:
		for idx in range(0, len(sents)):
			try:
				out_f.write(sents[idx] + camr[idx] + '\n')
				new_camr.append(camr[idx])
				new_jamr.append(jamr[idx])
				new_sents.append(sents[idx])
				new_f_scores.append(f_scores[idx])	
			except:		#ascii error
				pass	
	out_f.close()
	os.system('rm temp.txt')
	
	final_sents = []
	final_camr = []
	final_jamr = []
	final_f_scores = []
	
	for idx in range(0, len(new_camr)):
		if 'null_edge' not in new_camr[idx] and 'null_tag' not in new_camr[idx]:
			final_camr.append(new_camr[idx])
			final_jamr.append(new_jamr[idx])
			final_sents.append(new_sents[idx])
			final_f_scores.append(new_f_scores[idx])
	
	new_res = {}
	
	for idx in range(len(final_sents)):
		if final_sents[idx] not in new_res:
			new_res[final_sents[idx]] = [final_camr[idx], final_jamr[idx], final_f_scores[idx]]
	
	return new_res		
		


def get_num_words(sent):
	num_words = len([x for x in sent.strip().split() if len(x) > 1 or x.isalpha() or x.isdigit()])	#do not count punctuation
	return float(num_words)


def get_max_new(res):
	max_new = 0
	for key in res:
		if res[key][3] > max_new:
			max_new = res[key][3]
	
	return max_new		


def add_extra_score(res):
	
	for key in res:
		num_words = get_num_words(key)
		smatch_f = float(res[key][2])
		new_score = float(smatch_f / (1.0 / num_words))
		res[key].append(new_score)
	
	max_new = get_max_new(res)
	
	for key in res:
		normalized_new = float(res[key][3]) / float(max_new)
		res[key].append(normalized_new)
	
	return res


def get_res_dict():
	res = {}
	for root, dirs, files in os.walk(args.d):
		for f in files:
			if f.endswith('.dict'):
				f_path = os.path.join(root, f)
				with open(f_path, 'r') as in_f:
					temp_res = json.load(in_f)
				in_f.close()
				
				for key in temp_res:
					res[key] = temp_res[key]
	return res				


def shuffle_dependent_lists(lst1, lst2):
	assert(len(lst1) == len(lst2))
	
	num_list = [i for i in range(len(lst1))]	
	shuffle(num_list)						#random list of numbers
	new_lst1 = []
	new_lst2 = []
	
	for idx in num_list:
		new_lst1.append(lst1[idx])
		new_lst2.append(lst2[idx])
	
	return new_lst1, new_lst2	


def amrs_per_f_score(res, f_list, max_amrs):
	for min_f in f_list:
		keep_amrs  = []
		keep_sents = []
		for sent in res:
			if res[sent][2] >= min_f:
				keep_amrs.append(res[sent][0])
				keep_sents.append(sent.replace('# ::snt','').strip())
		print '\nFor minimal F-score of {0}:\n'.format(min_f)
		f_amr  = '{0}silver_camr_jamr_{1}.tf'.format(args.f1, min_f)
		f_sent = '{0}silver_camr_jamr_{1}.sent'.format(args.f1, min_f)
		avg_length = get_avg_sen_len(keep_sents)
		
		print 'Number of AMRs: {0}'.format(len(keep_sents))
		print 'Avg sen-len with null-tags: {0}'.format(avg_length)
		
		write_to_file(keep_amrs, f_amr)
		write_to_file(keep_sents, f_sent)
		
		if args.f2:			#also add constant number of AMRs per F-score if we specified a folder
			keep_amrs, keep_sents = shuffle_dependent_lists(keep_amrs, keep_sents)	#randomize 
			
			keep_amrs_const = keep_amrs[0:max_amrs]
			keep_sents_const = keep_sents[0:max_amrs]
			
			print 'Adding {0} AMRs for max_amrs of {1}'.format(len(keep_amrs_const), max_amrs)
			
			f_amr_const  = '{0}silver_camr_jamr_{1}_constant_{2}k.tf'.format(args.f2, min_f, int(max_amrs / 1000))
			f_sent_const = '{0}silver_camr_jamr_{1}_constant_{2}k.sent'.format(args.f2, min_f, int(max_amrs / 1000))
			
			write_to_file(keep_amrs_const, f_amr_const)
			write_to_file(keep_sents_const, f_sent_const)
			

def shuffle_bins(amr_bins):
	for idx in range(len(amr_bins)):
		shuffle(amr_bins[idx])
	
	return amr_bins	


def get_amrs_constant_F_score(res, f_list, added_amrs):
	amr_bins = [[] for i in range(len(f_list) -1)]
	
	for sent in res:
		f_score = res[sent][2]
		for idx in range(len(f_list) - 1):
			if f_score >= f_list[idx] and f_score < f_list[idx+1]:
				adding = res[sent]
				adding.append(sent)
				amr_bins[idx].append(adding)
	
	for to_add in added_amrs:
		amr_list = []
		loop_nr = 0
		amr_bins = shuffle_bins(amr_bins)		#shuffle bins so that we not add the same first few AMRs for each file
			
		while len(amr_list) < to_add:
			for idx in range(len(amr_bins)):
				amr_list.append(amr_bins[idx][loop_nr])
			loop_nr += 1
		
		amr_list = amr_list[0:to_add]
		
		final_sents = []
		final_amrs = []
		
		for val in amr_list:
			final_sents.append(val[3].replace('# ::snt','').strip())
			final_amrs.append(val[0])
		
		f_amr  = '{0}silver_camr_jamr_AMR_constant_{1}k.tf'.format(args.f3, int(to_add / 1000))
		f_sent = '{0}silver_camr_jamr_AMR_constant_{1}k.sent'.format(args.f3, int(to_add / 1000))
		
		write_to_file(final_amrs, f_amr)
		write_to_file(final_sents, f_sent)
		
				
	
def print_new_score_stats(res):
	div = range(0,50,5)
	div.append(1000)
	
	avg_smatch = []
	avg_new = []
	avg_norm = []
	avg_50 = []
	avg_60 = []
	avg_66 = []
	avg_75 = []
	avg_80 = []
	avg_85 = []
	avg_90 = []
	
	for idx in range(len(div)-1):
		instances, total_smatch, total_new, total_norm = 0,0,0,0
		for key in res:
			num_words = get_num_words(key)
			if num_words > div[idx] and num_words <= div[idx+1]:
				instances += 1
				total_smatch += res[key][2]
				total_new += res[key][3]
				total_norm += res[key][4]
		
		print 'For sentences ({2}) between {0} and {1} words'.format(div[idx], div[idx+1], instances)
		print 'Average smatch-score                  : {0}'.format(float(total_smatch) / float(instances))
		print 'Average senlen-based score            : {0}'.format(float(total_new) / float(instances))
		print 'Average normalized senlen-based score : {0}'.format(float(total_norm) / float(instances))
		print 'Weighted average 50/50                : {0}'.format((0.50 * float(total_smatch) / float(instances)) + (0.50 * float(total_norm) / float(instances)))
		print 'Weighted average 60/40                : {0}'.format((0.60 * float(total_smatch) / float(instances)) + (0.40 * float(total_norm) / float(instances)))
		print 'Weighted average 66/33                : {0}'.format((0.6666666 * float(total_smatch) / float(instances)) + (0.33333 * float(total_norm) / float(instances)))
		print 'Weighted average 75/25                : {0}'.format((0.75 * float(total_smatch) / float(instances)) + (0.25 * float(total_norm) / float(instances)))
		print 'Weighted average 80/20                : {0}'.format((0.80 * float(total_smatch) / float(instances)) + (0.20 * float(total_norm) / float(instances)))
		print 'Weighted average 85/20                : {0}'.format((0.85 * float(total_smatch) / float(instances)) + (0.15 * float(total_norm) / float(instances)))
		print 'Weighted average 90/10                : {0}\n'.format((0.90 * float(total_smatch) / float(instances)) + (0.10 * float(total_norm) / float(instances)))
		

		avg_smatch.append(round(float(total_smatch) / float(instances),3))
		avg_new.append(round(float(total_new) / float(instances),3))
		avg_norm.append(round(float(total_norm) / float(instances),3))
		avg_50.append(round((0.50 * float(total_smatch) / float(instances)) + (0.50 * float(total_norm) / float(instances)),3))
		avg_60.append(round((0.60 * float(total_smatch) / float(instances)) + (0.40 * float(total_norm) / float(instances)),3))
		avg_66.append(round((0.6666666 * float(total_smatch) / float(instances)) + (0.33333 * float(total_norm) / float(instances)),3))
		avg_75.append(round((0.75 * float(total_smatch) / float(instances)) + (0.25 * float(total_norm) / float(instances)),3))
		avg_80.append(round((0.80 * float(total_smatch) / float(instances)) + (0.20 * float(total_norm) / float(instances)),3))
		avg_85.append(round((0.85 * float(total_smatch) / float(instances)) + (0.15 * float(total_norm) / float(instances)),3))
		avg_90.append(round((0.90 * float(total_smatch) / float(instances)) + (0.10 * float(total_norm) / float(instances)),3))
	
	print 'avg_smatch', avg_smatch
	print 'avg_new', avg_new
	print 'avg_norm', avg_norm
	print 'avg_50', avg_50
	print 'avg_60', avg_60
	print 'avg_66', avg_66
	print 'avg_75', avg_75
	print 'avg_80', avg_80
	print 'avg_85', avg_85
	print 'avg_90', avg_90			

if __name__ == '__main__':
	if not args.dic:
		print 'Creating new dict...'
		res = get_res_dict()
		print 'Check for errors...'
		res = check_errors(res)
		
		with open(args.d + 'full_dict.dict', 'w') as out_f:	#dump created dict so we can load it next time to save time
			json.dump(res, out_f)
		out_f.close()	
	else:
		print 'Loading dict...'
		with open(args.dic) as in_f:    
			res = json.load(in_f)
		
	print 'Done with creating/loading dict'
	
	#res = add_extra_score(res)
	#print_new_score_stats(res)
	
	#f_list = [0.5, 0.55,0.60, 0.65, 0.7,0.75, 0.8, 0.85]
	#max_amrs = 25000
	#added_amrs = [10000, 20000, 30000, 40000, 50000, 75000, 100000]
	
	#amrs_per_f_score(res, f_list, max_amrs)
	
	#if args.f3:
	#	get_amrs_constant_F_score(res, f_list, added_amrs)
	
				
