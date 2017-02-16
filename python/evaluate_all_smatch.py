#!/usr/bin/env python

import os
import sys
import shlex
import subprocess
import argparse
from multiprocessing import Pool

'''Script that produces the Smatch output for CAMR, Boxer and Seq2seq produced AMRs'''

# python evaluate_all_smatch.py -g ~/Documents/amr_Rik/data_2017/data/amrs/split/ -mx 8 -seq_400 ./Seq2seq/output/1lay_400s_24k/ -seq_400_50k ./Seq2seq/output/1lay_400s_50k/ -seq_400_110k ./Seq2seq/output/1lay_400s_111k/ -seq_400_150k ./Seq2seq/output/1lay_400s_150k/ -seq_400_205k ./Seq2seq/output/1lay_400s_205k/

parser = argparse.ArgumentParser()
parser.add_argument('-g', required=True, type=str, help="Folder with gold AMR files")
parser.add_argument('-mx', required=False, type=int, default = 4, help="Number of maxthreads")
parser.add_argument('-rs', required=False, type=int, default = 4, help="Number of restarts for smatch")
parser.add_argument('-seq_400', required = False,type=str, default = './Seq2seq/working/',  help="Directory with produced seq2seq AMRs")
parser.add_argument('-seq_400_50k', required = False,type=str, default = './Seq2seq/working/',  help="Directory with produced seq2seq AMRs")
parser.add_argument('-seq_400_110k', required = False,type=str, default = './Seq2seq/working/',  help="Directory with produced seq2seq AMRs")
parser.add_argument('-seq_400_150k', required = False,type=str, default = './Seq2seq/working/',  help="Directory with produced seq2seq AMRs")
parser.add_argument('-seq_400_205k', required = False,type=str, default = './Seq2seq/working/',  help="Directory with produced seq2seq AMRs")
parser.add_argument('-box', required = False,type=str, default = './Boxer/working/', help="Directory with produced Boxer AMRs")
parser.add_argument('-cam', required = False,type=str, default = './CAMR/working/', help="Directory with produced old CAMR AMRs")
parser.add_argument('-cam_new', required = False,type=str, default = './CAMR/working_new/', help="Directory with produced new CAMR AMRs")
parser.add_argument('-default', required = False,type=str, default = './smart_default/', help="Directory with smart defaults")
parser.add_argument('-range_sen', nargs='+', type=int, default = [], help ='Range of sentence length [min max]')
parser.add_argument('-range_words', nargs='+', type=int, default = [], help ='Set range of words instead of chars [min max]')

args = parser.parse_args()

roots_to_check = [args.box, args.box, args.cam, args.cam_new,args.seq_400, args.seq_400,args.seq_400, args.seq_400_50k, args.seq_400_50k, args.seq_400_50k, args.seq_400_110k,args.seq_400_110k,args.seq_400_110k, args.seq_400_150k,args.seq_400_150k,args.seq_400_150k, args.seq_400_205k,args.seq_400_205k,args.seq_400_205k,args.default]
output_id = ['.amr.wiki','amr.wiki.corr.rel', '.parsed','.parsed','.seq.amr.restore','.seq.amr.restore.wiki','.seq.amr.restore.wiki.psp','.seq.amr.restore','.seq.amr.restore.wiki','.seq.amr.restore.wiki.psp','.seq.amr.restore','.seq.amr.restore.wiki','.seq.amr.restore.wiki.psp','.seq.amr.restore','.seq.amr.restore.wiki','.seq.amr.restore.wiki.psp','.seq.amr.restore','.seq.amr.restore.wiki','.seq.amr.restore.wiki.psp','.tf']
model_type = ['Boxer', 'Boxer Remap','CAMR (old)','CAMR (new)','Seq2 1l_400s_25k (no wiki)','Seq2 1l_400s_25k (wiki)','Seq2 1l_400s_25k (wiki + psp)','Seq2 1l_400s_50k (no wiki)','Seq2 1l_400s_50k (wiki)','Seq2 1l_400s_50k (wiki + psp)','Seq2 1l_400s_110k (no wiki)','Seq2 1l_400s_110k (wiki) ','Seq2 1l_400s_110k (wiki + psp)','Seq2 1l_400s_150k (no wiki)','Seq2 1l_400s_150k (wiki) ','Seq2 1l_400s_150k (wiki + psp)','Seq2 1l_400s_205k (no wiki)','Seq2 1l_400s_205k (wiki) ','Seq2 1l_400s_205k (wiki + psp)','Smart default']

if not (len(roots_to_check) == len(output_id) and len(roots_to_check) == len(model_type)):
	raise ValueError('Wrong set-up of the predefined lists')
else:
	print 'Lists are OK'	

def get_gold_ids(root, type_test):
	gold_ids = []
	gold_files = []
	for r, d, files in os.walk(root):
		for f in files:
			if '.txt' in f:
				gold_ids.append(f.split('-')[6].split('.')[0])
				gold_files.append(type_test+ f)
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


def evaluate(entry, ident, model, gold_ids, gold_files, res_dict, print_check):
	'''Will print smatch scores for Boxer, Seq2seq and CAMR'''
	print 'Model:', model
	
	if 'seq' in ident or 'Smart' in model:				# add one_line argument to smatch if it's seq2seq input
		one_line = '--one_line'
	else:
		one_line = ''	
	
	for root, dirs, files in os.walk(entry):
		for f in files:
			#print f
			if f!= [] and f.endswith(ident):			# often rubbish files in there, only find the file with the produced AMR
				for idn in gold_ids:		# check if it matches with a file in the gold map
					if idn in f:
						produced_f = os.path.join(root,f)
						gold_f = os.path.join(args.g, get_gold_file(idn, gold_files))
						
						if not args.range_sen and not args.range_words: # the normal output
							os_call = 'python ./Boxer/smatch_2.0.2/smatch.py -r 4 {2} -f {0} {1}'.format(produced_f, gold_f, one_line)
							output = subprocess.check_output(os_call, shell=True)
							f_score = output.split()[-1]		# get F-score from output
							num_sen = output.split()[-4]
							res_dict[model].append([idn, f_score, int(num_sen)])
						
						elif args.range_words and not args.range_sen:
							
							os_call = 'python ./Boxer/smatch_2.0.2/smatch_max_length.py -w1 {3} -w2 {4} -r 4 {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.range_words[0], args.range_words[1])	
							output = subprocess.check_output(os_call, shell=True)
							skipped_sen = output.split()[-7]
							total_sen = output.split()[-4]
							processed_sen = int(total_sen) - int(skipped_sen)
							f_score = output.split()[-1]		# get F-score from output
							if print_check == 0:
								print 'Skipped sentences for {0} : {1} out of {4} (range {2}-{3})'.format(f.split('-')[-1].replace('.txt',''), skipped_sen, args.range_words[0], args.range_words[1], total_sen)
							res_dict[model].append([idn, f_score, processed_sen])
						
						elif args.range_sen and not args.range_words:			# only calculate smatch score for sentences within a certain length range
							
							os_call = 'python ./Boxer/smatch_2.0.2/smatch_max_length.py -b1 {3} -b2 {4} -r 4 {2} -f {0} {1}'.format(produced_f, gold_f, one_line, args.range_sen[0], args.range_sen[1])	
							output = subprocess.check_output(os_call, shell=True)
							skipped_sen = output.split()[-7]
							total_sen = output.split()[-4]
							processed_sen = int(total_sen) - int(skipped_sen)
							f_score = output.split()[-1]		# get F-score from output
							if print_check == 0:
								print 'Skipped sentences for {0} : {1} out of {4} (range {2}-{3})'.format(f.split('-')[-1].replace('.txt',''), skipped_sen, args.range_sen[0], args.range_sen[1], total_sen)
							res_dict[model].append([idn, f_score, processed_sen])
						else:
							raise ValueError("Don't do both range_sen and range_words")	
		break				
	return res_dict					
		
						
def fix_res_list(all_res):
	return_res = []
	for idx in range(len(all_res[0])):
		return_res.append("\t".join(all_res[0][idx]) + '\t' +  "\t".join(all_res[1][idx]))
	
	return return_res	

def add_average(d):
	for key in d:
		total_f = 0
		total_sen = 0
		did_item = False
		for item in d[key]:
			did_item = True
			total_sen += item[2]
			total_f += float(item[2]) * float(item[1])
		if did_item:
			avg_f = round(float(total_f) / float(total_sen),3)
			d[key].append(['avg',str(avg_f),str(total_sen)])
		else:
			d[key].append(['avg','',''])	
	
	return d	

def print_nice_output(res_dict, gold_ids, model_type, type_test):
	gold_ids.append('avg')		#add for average
	print '\nResults for', type_test +':\n'
	print '\n\t\t\t\t' + "\t".join(gold_ids).replace('consensus','consen')  # last replace for nicer printing
	res_list = [[],[],[]]
	
	res_dict = add_average(res_dict)
	
	for m in model_type:
		num_tabs = int(((8*4) - len(m)) / 8) 
		print_l = m + num_tabs * '\t'
		for idn in gold_ids:					## test file options
			for key in res_dict:
				if key == m:					## we have the right model
					for item in res_dict[key]:
						if item[0] == idn:		## get right file
							print_l += '\t' + str(item[1])
		print print_l					
	
	#for idx,model in enumerate(model_type):
		#print_l = model
		#for key in res_dict:
			#print key
			#for ident in gold_ids:
				#if key == ident:
					#try:
						#print_l += '\t' + res_dict[key][idx]
						#res_list[idx].append(res_dict[key][idx])
					#except:
						#res_list[idx].append('NA')
						#print_l += '\t' + 'NA' # something went wrong but often on purpose, so print N/A	
		#print print_l		
	return res_list
	
	
def print_combined_output(res_list, gold_ids, test_types, model_type):
	gold_ids_both = [g + '-' + test_types[0].replace('/','') for g in gold_ids] + [g + '-' + test_types[1].replace('/','') for g in gold_ids]
	print '\nCombined results:\n\n\t' + "\t".join(gold_ids_both).replace('consensus','consen').replace('dfa-dev','dfa-dev ')  # last replace for nicer printing
	for idx, model in enumerate(model_type):
		print model + '\t' + res_list[idx].replace('\t','\t\t')
	print '\n'
		
		
if __name__ == '__main__':
	all_res = []
	#test_types = ['dev/','test/']
	test_types = ['test/']
	gold_ids = []
	
	for type_test in test_types:
		gold_input = args.g + type_test
		
		if not gold_ids:													# ugly fix to keep same order for the gold_ids when combining output
			gold_ids, gold_files = get_gold_ids(gold_input, type_test)
		else:
			throwaway_ids, gold_files = get_gold_ids(gold_input, type_test)	
		
		res_dict = create_res_dict(model_type)
		
		for idx, root in enumerate(roots_to_check):
			#if '_205k (wiki + psp)' in model_type[idx]:
			root_fix = root + type_test
			res_dict = evaluate(root_fix, output_id[idx], model_type[idx], gold_ids, gold_files, res_dict, idx)
			
		res_list = print_nice_output(res_dict, gold_ids, model_type, type_test)
		#all_res.append(res_list)
		
	#res_list = fix_res_list(all_res)
	#print_combined_output(res_list, gold_ids, test_types, model_type)	
