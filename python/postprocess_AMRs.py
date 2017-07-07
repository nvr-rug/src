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
parser.add_argument('-o', required = True,help="General output-folder")
parser.add_argument('-f', default = '',help="Working folder test, if empty we find it heuristically")
parser.add_argument("-OMT_path", default = '/home/p266548/Documents/amr_Rik/OpenNMT/', type=str, help="Path where we keep the OMT source files")
parser.add_argument("-prod_ext", default = '.seq.amr', type=str, help="Prod extension")
parser.add_argument("-sent_ext", default = '.sent', type=str, help="Sent extension")
parser.add_argument("-tgt_ext", default = '.char.tf', type=str, help="Target extension")
parser.add_argument("-python_path", default = '/home/p266548/Documents/amr_Rik/Seq2seq/src/python/', type=str, help="Path where we keep the python source files")
parser.add_argument('-nc', action='store_true', help='Not doing coreference, since we already do in the restore file')
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
	
	if not os.path.isfile(wiki_file):
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
	else:
		print '\t\tWiki file already exists, skipping...'
		log_file.write('\t\tWiki file already exists, skipping...')
		return wiki_file, True


def add_coreference(in_file, log_file, ext):
	log_file.write('\tAdding coreference..\n')
	coref_file = in_file + ext
	if not os.path.isfile(coref_file):
		coref_call = 'python ' + args.python_path + 'place_coreferents.py -f {0} -output_ext {1}'.format(in_file, ext)  #no wiki call
		os.system(coref_call)
	else:
		print '\t\tCoref file already exists, skipping...'	
		log_file.write('\t\tCoref file already exists, skipping...')
		
	return coref_file
	

def do_pruning(in_file, log_file):
	log_file.write('\tPruning...\n')
	prune_file = in_file + '.pruned'
	
	if not os.path.isfile(prune_file):
		prune_call = 'python ' + args.python_path + 'delete_double_args.py -f {0}'.format(in_file)
		os.system(prune_call)
		print 'prune file: {0}'.format(prune_file)
		check_valid(prune_file, True, log_file)
	else:
		print '\t\tPrune file already exists, skipping'	
		log_file.write('\t\tPrune file already exists, skipping')
		
	return prune_file


def restore_amr(in_file, output_direc, file_path, log_file):
	log_file.write('\tRestoring...\n')
	restore_file = output_direc + '/' + in_file + '.restore'
	
	if not os.path.isfile(restore_file):
	
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
	else:
		print '\t\tRestore file already exists, skipping...'
		log_file.write('\t\tRestore file already exists, skipping...')	
	
	return restore_file


def check_invalid(in_file, log_file):
	log_file.write('\tDeleting invalid args...\n')
	out_ext = '.check'
	check_file = in_file + out_ext
	
	if not os.path.isfile(check_file):
		check_call = 'python ' + args.python_path + 'delete_invalid_args.py -f {0} -out_ext {1}'.format(in_file, out_ext)
		os.system(check_call)
	else:
		print '\t\tCheck invalid file (.check) already exists, skipping...'	
		log_file.write('\t\tCheck invalid file (.check) already exists, skipping...')
		
	return check_file


def get_check_dirs(output_folder):
	folders = next(os.walk(output_folder))[1]
	full_folders = [os.path.join(output_folder, x) for x in folders]
	
	to_do = []
	
	for fol in full_folders:
		do_folder = False
		for root, dirs, files in os.walk(fol):
			for f in files:
				if f.endswith(args.prod_ext):
					f_path = os.path.join(root, f + '.restore')
					if not (os.path.isfile(f_path) and os.path.isfile(f_path + '.pruned') and  os.path.isfile(f_path + '.check') and  os.path.isfile(f_path + '.coref') and (os.path.isfile(f_path + '.wiki') or os.path.isfile(f_path + '.failed_wiki'))):
						do_folder = True
		
		if do_folder:
			to_do.append(fol)
	
	print 'Doing {0} out of {1} folders'.format(len(to_do), len(full_folders))
	return to_do		

def process_dir(output_direc):
	'''Postprocessing AMR folders'''

	log_folder, log_file = get_logs(output_direc)
	
	if 'dev' in args.o:
		sent_folder = args.o.replace('/output_dev','/working/dev')
	elif 'bio' in args.o.lower():
		sent_folder = args.o.replace('/output','/working/test')
	else:
		sent_folder = '/home/p266548/Documents/amr_Rik/data_2017_fixed_unicode/data/amrs/split/test/'	
	
	with open(log_file, 'w') as f_out:	
		for root, dirs, files in os.walk(output_direc):
			for f in files:
				if f.endswith(args.prod_ext):
					file_path = os.path.join(root,f)
					if os.path.getsize(file_path) > 0: #check if file has content
					
						f_out.write('Processing steps of {0}\n'.format(f))
						print 'Processing steps of {0}\n'.format(f)
						
						if 'dev' in args.o:
							if 'bio' in args.o.lower():
								sent_file = sent_folder + 'bio_dev_amrs.sent'
							else:
								sent_file = sent_folder + 'created_dev.sent.gold' 
						else:
							if 'bio' in args.o.lower():
								sent_file = sent_folder + 'bio_test_amrs.sent'
							else:	
								sent_file = sent_folder + f.replace(args.prod_ext, '.sent').replace('.char.sent','.sent')
						
						if not os.path.isfile(sent_file):
							print sent_file
							print 'Something is wrong, sent-file does not exist'	
						# first do postprocessing steps individually
						
						restore_file 		= restore_amr(f, output_direc, file_path, f_out)
						check_file			= check_invalid(restore_file, f_out)
						prune_file 			= do_pruning(restore_file, f_out)
						if not args.nc:
							coref_file 		= add_coreference(restore_file, f_out, '.coref')
						
						wiki_file, success 	= add_wikification(restore_file, sent_file, f_out)
						
						#then add all postprocessing steps together, starting at the pruning
						
						f_out.write('\tDo all postprocessing steps...\n')
						print '\tDo all postprocessing steps...\n'
						
						check_file_pruned = do_pruning(check_file, f_out) 
						wiki_file_pruned, success = add_wikification(check_file_pruned, sent_file, f_out)
						
						if success:
							if not args.nc:
								coref_file_wiki_pruned 	  = add_coreference(wiki_file_pruned, f_out, '.coref.all')
							else:	#we already did coreference in restore file, still call the output-file .coref.all to not get confused in evaluation, just copy previous file
								os.system("cp {0} {1}".format(wiki_file_pruned, wiki_file_pruned + '.coref.all'))	
						else:
							f_out.write('\tWikification failed, not doing coreference on top of it\n')	
						
						f_out.write('\tDone processing!\n')
						print '\tDone processing!\n'			


def create_dev_files():
	sent_folder = args.o.replace('/output_dev','/working/dev')
	if 'dev' in args.o:
		sent_file = sent_folder + 'created_dev.sent.gold'
		if not os.path.isfile(sent_file):
			os_call = 'python ' + args.python_path + 'create_dev_file_again.py -g {0} -d {1}'.format('/home/p266548/Documents/amr_Rik/data_2017_fixed_unicode/data/amrs/split/dev/', sent_folder)
			os.system(os_call)
		if not os.path.isfile(sent_file):
			print 'Creation did not work apparently (something went wrong), exiting'
			sys.exit(0)	 

	
if __name__ == "__main__":
	check_dirs = get_check_dirs(args.o)
	
	if 'dev' in args.o and 'bio' not in args.o.lower():
		create_dev_files()
	
	max_processes = min(len(check_dirs), 12)
	#max_processes = 1
	print 'Processing {0} dirs, {1} in parallel'.format(len(check_dirs), max_processes)
	
	pool = Pool(processes=max_processes)						
	pool.map(process_dir, check_dirs)						# process directories in parallel		
				
									
	
	
	
	
	
	

