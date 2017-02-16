import re,sys, argparse, os, random, collections, subprocess, json
import validator_seq2seq

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="All AMR file to use in the ensemble")
parser.add_argument("-t", required = True, type=str, help="test-file with gold-data")
args = parser.parse_args()


def validate_with_rewrite(f):
	new_lines = []
	errors = 0
	prev_line = ''
	for line in open(f,'r'):
		if not validator_seq2seq.valid_amr(line):
			new_lines.append(prev_line.strip())
			errors += 1
		else:
			new_lines.append(line.strip())
		
		prev_line = line
	
	with open(f,'w') as out_f:
		for l in new_lines:
			out_f.write(l.strip() + '\n')
	out_f.close()					
	
	print 'Rewrote {0} AMRs for {1}'.format(errors, f)		

def get_smatch(f1, f2, one_line):
	f1 += '.print'
	if 'bio_test_amrs' not in f2:
		f2 += '.print'
	os_call = 'python /home/p266548/Documents/amr_Rik/smatch/smatch.py --significant 5 -r 4 -f {0} {1}'.format(f1,f2)
	
	output = subprocess.check_output(os_call, shell=True)
	f_score = float(output.split()[-1])
	#print f_score           
	return f_score

def get_best_amr(res):
	ok = 1


def add_to_dict(value, key, d):
	if key in d:
		d[key].append(value)
	else:
		d[key] = [value]
	
	return d


def write_to_file(f, string):
	with open(f, 'w') as out_f:
		out_f.write(string.strip() + '\n')
	out_f.close()	


def get_amrs_in_dict(walk_dir):
	parse_dict = {}
	for root, dirs, files in os.walk(walk_dir):
		for f in files:
			if 'temp' not in f and 'print' not in f and ('nonull' in f or 'seq' in f):
				f_path = os.path.join(root, f)
				validate_with_rewrite(f_path)					#rewrite invalid AMRs to previous AMR
				amrs = [x.strip() for x in open(f_path, 'r')]
				len_amrs = len(amrs)
				parse_dict[f] = amrs
	
	for idx, key in enumerate(parse_dict):
		print idx, key
	
	return parse_dict, len_amrs	


def get_amr_list(parse_dict, len_amrs):
	amr_list = []
	
	for idx in range(len_amrs):
		add_list = []
		for key in parse_dict:
			add_list.append(parse_dict[key][idx])
		amr_list.append(add_list)
	
	return amr_list	


def get_most_similar_amr(already_done):
	best_score = 0
	best_key = None
	best_idx = None
	
	for key in already_done:			
		f_list = [x[0] for x in already_done[key]]
		avg_score = float(sum(f_list)) / float(len(f_list))
		keep_idx = already_done[key][0][1]
		if avg_score > best_score:
			best_score = avg_score
			best_key = key
			best_idx = keep_idx
	
	if best_key and best_score != 0:
		return [best_key, best_score, best_idx]
	else:
		print best_key, best_score, best_idx
		raise ValueError ("Something is wrong, already_done dict probably empty")			


def get_best_amrs(amr_list):
	best_amrs = []
	
	for count, item in enumerate(amr_list):
		if count % 50 == 0:
			print count
		already_done = {}
		
		for idx, val in enumerate(item):		#check if they are valid, if not, ignore
			if not validator_seq2seq.valid_amr(val):
				item[idx] = 'INVALID'
				print 'Error in file'
		
		for idx1 in range(len(item)):
			for idx2 in range(idx1 + 1, len(item)):	
				if item[idx1] == 'INVALID' or item[idx2] == 'INVALID':
					f_score = 0.0
				else:
					write_to_file(args.f + 'temp1.txt', item[idx1])
					write_to_file(args.f +'temp2.txt', item[idx2])
					os.system('python reformat_single_amrs.py -f ' + args.f + 'temp1.txt')
					os.system('python reformat_single_amrs.py -f ' + args.f + 'temp2.txt')
					f_score = get_smatch(args.f + 'temp1.txt', args.f + 'temp2.txt', '--both_one_line')

			
				already_done = add_to_dict([f_score, idx1], item[idx1], already_done)	# save results
				already_done = add_to_dict([f_score, idx2], item[idx2], already_done)	
					
		most_similar_amr = get_most_similar_amr(already_done)
		best_amrs.append(most_similar_amr)
	
	
	return best_amrs


def print_ensemble_stats(best_amrs):
	model_list = [x[2] for x in best_amrs]
	model_count=collections.Counter(model_list)
	
	for k in model_count:
		print k, model_count[k]
	
	return model_list	


def print_original_smatch_scores(walk_dir):
	f_scores = []
	for root, dirs, files in os.walk(walk_dir):
		for f in files:				
			if 'temp' not in f and 'print' not in f and ('nonull' in f or 'seq' in f):
				f_path = os.path.join(root, f)
				f_score = get_smatch(f_path, args.t, '--one_line')
				f_scores.append(f_score)
				print 'F-score {0} = {1}'.format(f, f_score)
	return f_scores		


def ensemble_fscore(model_list):
	#f_name = '/home/p266548/Documents/amr_Rik/sem_eval_testdata/ensemble_eval_nonull//ensemble_' + args.f.split('/')[-2]
	#f_name = '/home/p266548/Documents/amr_Rik/sem_eval_testdata/ensemble_results_eval/ensemble_' + args.f.split('/')[-2]
	f_name = '/home/p266548/Documents/amr_Rik/sem_eval_testdata/ensembles/test/ensemble_new_smatch/ensemble_' + args.f.split('/')[-2]
	#f_name = '/home/p266548/Documents/amr_Rik/sem_eval_testdata/ensembles/eval/ensemble_eval_nonull_new_smatch/ensemble_' + args.f.split('/')[-2]
	
	#print 'Printed ensemble AMRs to {0}'.format(f_name)
	
	with open(f_name, 'w') as out_f:
		for item in model_list:
			out_f.write(item[0].strip() + '\n')
	out_f.close()
	
	os.system('python reformat_single_amrs.py -f {0}'.format(f_name))
			
	f_score = get_smatch(f_name , args.t, '--one_line')
	print 'F-score ensemble = {0}'.format(f_score)
	#return 0
	return f_score		


if __name__ == '__main__':
	
	#parse_dict, len_amrs = get_amrs_in_dict(args.f)					#get all 500 AMRs per file
	#amr_list   			 = get_amr_list(parse_dict, len_amrs) 		#get lists of lists with AMR per sentence
	#best_amrs            = get_best_amrs(amr_list)					#get most similar to other AMRs
	#model_list = print_ensemble_stats(best_amrs)					#print which AMRs we took
	
	f_scores = print_original_smatch_scores(args.f)				#get original scores for comparison
	#ensemble_f = ensemble_fscore(best_amrs)						#get F-score of ensemble
	
	#if max(f_scores) < 	ensemble_f:
	#	print 'Succes, ensemble beats max F-score: {1} vs {0}'.format(max(f_scores), ensemble_f)
	#else:
	#	print 'Fail, ensemble is words than max F-score: {1} vs {0}'.format(max(f_scores), ensemble_f)	
						
