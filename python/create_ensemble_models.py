#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script that creates averaged (ensembled) models out of list of multiple models'''

import re,sys, argparse, os, random, collections, subprocess, json
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="Model folder")
parser.add_argument("-script", required = False, default = '/home/p266548/Documents/amr_Rik/OpenNMT/tools/average_models.lua', type=str, help="Script to average")
parser.add_argument("-model_ext", required = False, default = '.t7', type=str, help="Model extension")
parser.add_argument("-max_epoch", required = False, default = 100, type=int, help="Ignore epochs after this number - do this when we accidentally trained for too long")
parser.add_argument("-min_last", required = False, default = 2, type=int, help="Minimal number of models to average for last X models")
parser.add_argument("-max_last", required = False, default = 6, type=int, help="Maximal number of models to average for last X models")
parser.add_argument("-max_num", required = False, default = 5, type=int, help="Max number of models in total for same ppx models for certain threshold")
parser.add_argument("-min_num_ppx", required = False, default = 4, type=int, help="Min number of models to average for same ppx models for certain threshold")
parser.add_argument("-print_only", required = False, action = 'store_true', help="If true only print models we want to create - don't actually create them")
args = parser.parse_args()


def average_models(models, output_file):
	'''Create average model here'''
	
	sub_call = ["lua", args.script,'-models'] + models + ['-output_model',output_file, '-gpuid','1']
	
	if not os.path.isfile(output_file):	#don't do this is output file already exists
		if args.print_only:
			print 'Create', output_file
		else:	
			subprocess.call(sub_call)
	else:
		print 'Dont create {0}, exists already'.format(output_file)	


def average_last_models(sorted_models, threshold):
	'''Select the X last number of models to average out'''
	
	selected = sorted_models[len(sorted_models) - threshold :]
	models 	 = [x[0] for x in selected]
	epochs   = "_".join([str(x[3]) for x in selected])
	out_file = selected[0][1] + 'model_ensemble_{0}_last_epochs_{1}.t7'.format(threshold, epochs)
	
	average_models(models, out_file)


def average_ppx_models(ppx_models):
	'''Average the selected ppx models'''
	
	models 	 = [x[0] for x in ppx_models]
	epochs   = "_".join([str(x[3]) for x in ppx_models])
	out_file = ppx_models[0][1] + 'model_ensemble_ppx_epochs_{0}.t7'.format(epochs)
	
	average_models(models, out_file)
	

def get_same_ppx_models(sorted_models):
	'''Get all best models until perplexity goes up'''
	
	ppx_models = []
	count = 0
	
	for m in reversed(sorted_models):
		if count == 0:				#always add first model
			ppx_models.append(m)
		else:
			if m[4] <= prev_ppx:	#compare perplexities
				ppx_models.append(m)	
			else:
				break		#ppx is different (higher, so worse), therefore break	
		
		prev_ppx = m[4]		#save prev ppx
		count += 1
	
	return ppx_models[::-1]	#reverse order again


def fill_random_list(ppx_models, threshold, max_num):
	'''Out of a list of X elements, select subsets of threshold elements. Only do this max_num times at the most
	   E.g. out of [1,2,3,4,5,6], select [1,4,5], [2,5,6] and [1,2,5]'''
	
	return_list = []
	counter = 0
	
	while len(return_list) < max_num and counter < 100:		#try max a 100 times
		sample = random.sample(ppx_models, threshold)
		sorted_sample = sorted(sample, key = lambda x:x[3])	#sort so we keep the order of epochs
		if sorted_sample not in return_list:
			return_list.append(sorted_sample)
		counter += 1	
	
	print 'Avg models with same ppx (threshold {0}) - max {1}, total {2}'.format(threshold, max_num, len(return_list))
	
	return return_list			


def average_same_ppx(ppx_models, threshold):
	if threshold <= len(ppx_models):	#only do this if we can pick threshold number of items - should never happen
		picked_combinations = fill_random_list(ppx_models, threshold, args.max_num)
		for comb in picked_combinations: #make ensemble out of each of the combinations
			average_ppx_models(comb)	#actually average ensemble 
		
			
if __name__ == '__main__':
	
	models = []
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith('.t7') and '_ensemble_' not in f:			#assumes model files look like this: model_epoch13_1.19.t7 - program will fail otherwise
				f_path = os.path.join(root, f)
				epoch = int(re.findall(r'epoch([\d]+)',f)[0]) 
				ppx = float(re.findall(r'_([\d]+\.[\d]+)',f)[0])
				if epoch <= args.max_epoch:							#check if epoch is within range
					models.append([f_path, root, f, epoch, ppx])
	
	sorted_models = sorted(models, key = lambda x:x[3])	#sort by epochs
	
	#average last X models in range
	
	for threshold in range(args.min_last, args.max_last + 1):
		print 'Average {0} last models\n'.format(threshold)
		average_last_models(sorted_models, threshold)
	
	#combinations of models with same perplexity
	
	same_ppx_models = get_same_ppx_models(sorted_models)
	
	for min_num in range(args.min_num_ppx, len(same_ppx_models) + 1):
		average_same_ppx(same_ppx_models, min_num)
