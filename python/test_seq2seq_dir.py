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
parser.add_argument("-f", required=True, type=str, help="folder that contains to be processed files (dev or test)")
parser.add_argument('-df', required = True,help="data folder for seq2seq model")
parser.add_argument('-tf', required = True,help="Folder that contains all checkpoints (actual models)")
parser.add_argument('-sf', required = True,help="Folder where we save all our output folders")
parser.add_argument('-size',default = 400, type = int ,help="size of model")
parser.add_argument('-en_vocab_size',default = 140, type = int ,help="Size of en vocab")
parser.add_argument('-fr_vocab_size',default = 140, type = int ,help="Size of fr vocab")
parser.add_argument('-layers',default = 1, type = int ,help="number of layers in model")
parser.add_argument('-max_threads',default = 8, type = int ,help="Max num of parallel threads for testing")
parser.add_argument('-no_rewrite',default = False, type = bool ,help="When included we rewrite invalid AMRs")
parser.add_argument("-prod_ext", default = '.seq.amr', type=str, help="Extension of produced AMRs (default .seq.amr)")
parser.add_argument("-input_ext", default = '.sent', type=str, help="Input extension (default .sent)")
parser.add_argument("-sent_ext", default = '.sent', type=str, help="Sent extension (default .sent)")
parser.add_argument("-output_ext", default = '.tf', type=str, help="Output extension (default .tf)")
parser.add_argument("-python_path", default = '/home/p266548/Documents/amr_Rik/Seq2seq/src/python/', type=str, help="Path where we keep the Python source files")
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
	check_valid(prune_file, True, log_file)
	
	return prune_file


def restore_amr(in_file, output_direc, file_path, log_file):
	log_file.write('\tRestoring...\n')
	restore_file = output_direc + '/' + in_file + '.restore'
	restore_call = 'python ' + args.python_path + 'restoreAMR/restore_amr.py {0} > {1}'.format(file_path, restore_file)
	os.system(restore_call)
	
							
	log_file.write('\tValidating...\n')
	check_valid(restore_file, True, log_file)
	
	return restore_file


def process_dir(cp_direc):
	'''Processes a checkpoint directory - producing output for all test files'''
	direc_name = cp_direc.split('/')[-2]
	output_direc = args.sf + 'output_' + direc_name
	if True:
	#if not os.path.isdir(output_direc):					# only do it if there is no folder already
		os.system('mkdir -p {0}'.format(output_direc))	# create output dir for this checkpoint
		log_file = output_direc +'/log.txt'
		print 'Starting testing {0}...time: {1}'.format(cp_direc,str(datetime.now()))
		with open(log_file, 'w') as f_out:
			#f_out.write('Starting testing {0}...\n'.format(cp_direc))
			#test_call = 'python ' + args.python_path + 'translate.py --multiple_files --decode --test_folder {5} --out_folder {4} --data_dir {0} --train_dir {1} --size={2} --num_layers={3} --log_file {6} --input_ext {7} --output_ext {8} --en_vocab_size {9} --fr_vocab_size {10} --test_ext {7}'.format(args.df, cp_direc, args.size, args.layers, output_direc, args.f, log_file, args.input_ext, args.output_ext, args.en_vocab_size, args.fr_vocab_size)
			#os.system(test_call)	#do python testing with file
			#f_out.write('Testing complete!\n')
			
			for root, dirs, files in os.walk(output_direc):
				for f in files:
					if f.endswith(args.prod_ext):
						f_out.write('Single processing steps of {0}\n'.format(f))
						file_path = os.path.join(root,f)
						sent_file = args.f + f.replace(args.prod_ext, args.sent_ext)		#find correct input file in working folder by replacing produced extension by the sent extension
						
						# first do postprocessing steps individually
						
						restore_file 		= restore_amr(f, output_direc, file_path, f_out)
						prune_file 			= do_pruning(restore_file, f_out)
						wiki_file, success 	= add_wikification(restore_file, sent_file, f_out)
						coref_file 			= add_coreference(restore_file, f_out, '.coref')
						
						# then add all postprocessing steps together, starting at the pruning
						
						f_out.write('\tDo all postprocessing steps...\n')
						
						wiki_file_pruned, success = add_wikification(prune_file, sent_file, f_out)
						if success:
							coref_file_wiki_pruned 	  = add_coreference(wiki_file_pruned, f_out, '.coref.all')
						else:
							f_out.write('\tWikification failed, not doing coreference on top of it\n')	
						
						f_out.write('\tDone processing!\n')
		f_out.close()				
	
if __name__ == "__main__":
	#dirs_to_check = os.walk(args.tf).next()[1]					# vocab folder and to be tested files stay the same, loop over different checkpoint models
	#max_processes = min(len(dirs_to_check), args.max_threads)
	#print '\nDoing {0} folders in parallel for {1} folders\n'.format(max_processes, len(dirs_to_check))
	#pool = Pool(processes=max_processes)						
	#pool.map(process_dir, dirs_to_check)						# test directories in parallel
	process_dir(args.tf)					
	#print args.tf			
					
									
	
	
	
	
	
	
