import sys
import re
import argparse
import os
import subprocess
import validator_seq2seq
import wikification_seq2seq
from multiprocessing import Pool
from datetime import datetime

'''Script that tests given seq2seq model on given test data, also restoring and wikifying the produced AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument('-f', required = True,help="Source files to be tested")
parser.add_argument('-test_ext', default = '.char.sent',help="Extension of to be tested files")
parser.add_argument('-tf', required = True,help="Specific model-file")
parser.add_argument('-o', required = True,help="General output-folder")
parser.add_argument('-beam_size', default = '5', type=str,help="Beam size")
parser.add_argument("-OMT_path", default = '/home/p266548/Documents/amr_Rik/OpenNMT/', type=str, help="Path where we keep the OMT source files")
parser.add_argument("-repl", default = '', type=str, help="Replacing unknowns yes/no? Default is empty meaning no")
parser.add_argument("-gpu", default = '', type=str, help="Testing on GPU?")
parser.add_argument("-max_sent_length", default = '500', type=str, help="Maximum sentence length")
parser.add_argument("-n_best", default = '1', type=str, help="Output n_best output AMRs instead of only 1")
parser.add_argument("-prod_ext", default = '.seq.amr', type=str, help="Output n_best output AMRs instead of only 1")
parser.add_argument("-sent_ext", default = '.sent', type=str, help="Sent extension")
parser.add_argument("-tgt_ext", default = '.char.tf', type=str, help="Target extension")
parser.add_argument("-python_path", default = '/home/p266548/Documents/amr_Rik/Seq2seq/src/python/', type=str, help="Path where we keep the python source files")
args = parser.parse_args() 


def get_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	return default


def check_valid(restore_file, rewrite, f_out):
	'''Checks whether the AMRS in a file are valid, possibly rewrites to default AMR'''
	
	idx = 0
	warnings = 0
	all_amrs = []
	for line in open(restore_file,'r'):
		idx += 1
		if not validator_seq2seq.valid_amr(line):
			f_out.write('\t\tError or warning in line {0}, write default\n'.format(idx))
			warnings += 1
			default_amr = get_default_amr()
			all_amrs.append(default_amr)		## add default when error
		else:
			all_amrs.append(line)	
	
	if warnings == 0:
		f_out.write('\t\tNo badly formed AMRs!\n')
	elif rewrite:
		f_out.write('\t\tRewriting {0} AMRs with error to default AMR\n'.format(warnings))
		
		with open(restore_file,'w') as out_f:
			for line in all_amrs:
				out_f.write(line.strip()+'\n')
		out_f.close()		
	else:
		f_out.write('\t\t{0} AMRs with warning - no rewriting to default\n'.format(warnings))	


def get_logs(output_direc):
	log_folder = "{0}/log".format(output_direc)
	log_file = log_folder + '/' + '/log_postprocessing.txt'
	os.system("mkdir -p {0}".format(log_folder))
	return log_folder, log_file


def add_wikification(in_file, sent_file, log_file):
	log_file.write('\tDoing Wikification...\n')
	wiki_file = in_file + '.wiki'
	wikification_seq2seq.wikify_pipeline_output(in_file, 'dbpedia', sent_file, log_file)
	
	num_sents = len([x for x in open(sent_file,'r')])	#for checking whether Wikification succeeded
	num_wiki = len([x for x in open(wiki_file,'r')])
	
	if num_sents != num_wiki:
		log_file.write('\t\tWikification failed for some reason (length {0} instead of {1})\n\t\tSave file as backup with wrong extension, no validating\n')
		os.system('mv {0} {1}'.format(wiki_file, wiki_file.replace('.wiki','.failed_wiki')))
		return wiki_file, False
	else:
		log_file.write('\tValidating again...\n')
		check_valid(wiki_file, True, log_file)
	
		return wiki_file, True	


def add_coreference(in_file, log_file, ext):
	log_file.write('\tAdding coreference..\n')
	coref_call = 'python ' + args.python_path + 'place_coreferents.py -f {0} -output_ext {1}'.format(in_file, ext)  #no wiki call
	os.system(coref_call)
	coref_file = in_file + ext
	
	return coref_file
	

def do_pruning(in_file, log_file):
	log_file.write('\tPruning...\n')
	prune_call = 'python ' + args.python_path + 'delete_double_args.py -f {0}'.format(in_file)
	os.system(prune_call)
	prune_file = in_file + '.pruned'
	print 'prune file: {0}'.format(prune_file)
	check_valid(prune_file, True, log_file)
	
	return prune_file


def restore_amr(in_file, output_direc, file_path, log_file):
	log_file.write('\tRestoring...\n')
	restore_file = output_direc + '/' + in_file + '.restore'
	if args.tgt_ext.endswith('.brack'):	#do something different in restoring if it is a tf.brack file
		restore_call = 'python ' + args.python_path + 'restoreAMR/restore_amr.py {0} brack > {1}'.format(file_path, restore_file)
		print '.brack file'
	elif args.tgt_ext.endswith('.brackboth'):
		restore_call = 'python ' + args.python_path + 'restoreAMR/restore_amr.py {0} brackboth > {1}'.format(file_path, restore_file)
		print '.brackboth file'
	else:
		restore_call = 'python ' + args.python_path + 'restoreAMR/restore_amr.py {0} > {1}'.format(file_path, restore_file)
	#print restore_call
	os.system(restore_call)
						
	log_file.write('\tValidating...\n')
	check_valid(restore_file, True, log_file)
	
	return restore_file


def check_invalid(in_file, log_file):
	log_file.write('\tDeleting invalid args...\n')
	out_ext = '.check'
	check_call = 'python ' + args.python_path + 'delete_invalid_args.py -f {0} -out_ext {1}'.format(in_file, out_ext)
	os.system(check_call)
	check_file = in_file + out_ext
	return check_file

def process_dir(cp_direc):
	'''Processes a checkpoint directory - producing output for all test files'''

	replace_unk = '-replace_unk' if args.repl else ''	
	gpu = '-gpuid 1' if args.gpu else ''
	direc_name 		= cp_direc.split('/')[-1]
	output_direc 	= args.o + 'output_' + direc_name
	log_folder, log_file = get_logs(output_direc)
	
	os.system('mkdir -p {0}'.format(output_direc))	# create output dir for this checkpoint
	
	print 'Starting testing {0}...time: {1}'.format(cp_direc,str(datetime.now()))
	
	with open(log_file, 'w') as f_out:
		for root, dirs, files in os.walk(args.f):
			for f in files:
				if f.endswith(args.test_ext):
					f_path = os.path.join(root, f)
					out_file = output_direc + '/' + f.replace(args.test_ext,args.prod_ext)
					log_output = log_folder + '/' +  f + '.log'
					
					f_out.write('Starting testing {0}...\n'.format(f))
					print 'Starting testing {0}...\n'.format(f)
					
					test_call = 'th {0}translate.lua -src {1} -output {2} -model {3} -beam_size {4} -max_sent_length {5} {6} -n_best {7} {8} -log_file {9} -fallback_to_cpu'.format(args.OMT_path, f_path, out_file, args.tf, args.beam_size, args.max_sent_length, replace_unk, args.n_best, gpu, log_output)
					os.system(test_call)	#do python testing with file
					
					f_out.write('Testing complete!\n')
					print 'Testing complete!\n'
		
		for root, dirs, files in os.walk(output_direc):
			for f in files:
				if f.endswith(args.prod_ext):
					f_out.write('Processing steps of {0}\n'.format(f))
					print 'Processing steps of {0}\n'.format(f)
					
					file_path = os.path.join(root,f)
					sent_file = args.f + f.replace(args.prod_ext, args.sent_ext)		#find correct input file in working folder by replacing produced extension by the sent extension
					
					# first do postprocessing steps individually
					
					restore_file 		= restore_amr(f, output_direc, file_path, f_out)
					check_file			= check_invalid(restore_file, f_out)
					prune_file 			= do_pruning(restore_file, f_out)
					wiki_file, success 	= add_wikification(restore_file, sent_file, f_out)
					coref_file 			= add_coreference(restore_file, f_out, '.coref')
					
					# then add all postprocessing steps together, starting at the pruning
					
					f_out.write('\tDo all postprocessing steps...\n')
					print '\tDo all postprocessing steps...\n'
					
					check_file_pruned = do_pruning(check_file, f_out) 
					wiki_file_pruned, success = add_wikification(check_file_pruned, sent_file, f_out)
					
					if success:
						coref_file_wiki_pruned 	  = add_coreference(wiki_file_pruned, f_out, '.coref.all')
					else:
						f_out.write('\tWikification failed, not doing coreference on top of it\n')	
					
					f_out.write('\tDone processing!\n')
					print '\tDone processing!\n'
	#f_out.close()				
	
if __name__ == "__main__":
	process_dir(args.tf)					
				
									
	
	
	
	
	
	
