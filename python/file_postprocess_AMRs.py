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
parser.add_argument("-sf", required = True, type=str, help="Sent folder")
parser.add_argument("-python_path", default = '/home/p266548/Documents/amr_Rik/Seq2seq/src/python/', type=str, help="Path where we keep the python source files")
args = parser.parse_args() 


def get_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	return default


def check_valid(restore_file, rewrite, f_out, sent_file):
	'''Checks whether the AMRS in a file are valid, removes invalid AMRs and sentences'''
	
	warnings = 0
	all_amrs = []
	sents = [x.strip() for x in open(sent_file,'r')]
	new_sents = []
	for idx, line in enumerate(open(restore_file,'r')):
		if not validator_seq2seq.valid_amr(line):
			f_out.write('\t\tError or warning in line {0}, write default\n'.format(idx))
			warnings += 1
		else:
			all_amrs.append(line)
			new_sents.append(sents[idx])	
	
	if warnings == 0:
		f_out.write('\t\tNo badly formed AMRs!\n')
		
	else:
		f_out.write('\t\tRemoved {0} invalid AMRs/sentences\n'.format(warnings))
	
	if not sent_file.endswith('.fil'):
		out_sent = sent_file + '.fil'
	else:
		out_sent = sent_file	
	
	with open(out_sent,'w') as out_s:
		for s in new_sents:
			out_s.write(s.strip() + '\n')
	out_s.close()
	
	with open(restore_file,'w') as out_a:
		for a in all_amrs:
			out_a.write(a.strip() + '\n')
	out_a.close()
		
	
	return out_sent			
			
	


def get_logs(output_direc):
	log_folder = "{0}/log".format(output_direc)
	log_file = log_folder + '/' + '/log_postprocessing.txt'
	os.system("mkdir -p {0}".format(log_folder))
	return log_folder, log_file



def add_coreference(in_file, log_file, ext):
	log_file.write('\tAdding coreference..\n')
	coref_file = in_file + ext
	coref_call = 'python ' + args.python_path + 'place_coreferents.py -f {0} -output_ext {1}'.format(in_file, ext)  #no wiki call
	os.system(coref_call)
		
	return coref_file
	

def do_pruning(in_file, log_file, sent_file):
	log_file.write('\tPruning...\n')
	prune_file = in_file + '.pruned'
	
	prune_call = 'python ' + args.python_path + 'delete_double_args.py -f {0}'.format(in_file)
	os.system(prune_call)
	print 'prune file: {0}'.format(prune_file)
	out_sent = check_valid(prune_file, True, log_file, sent_file)
	
	return prune_file, out_sent


def restore_amr(file_path, log_file, sent_file):
	log_file.write('\tRestoring...\n')
	restore_file = file_path + '.restore'
	
	
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
	out_sent = check_valid(restore_file, True, log_file, sent_file)
	return restore_file, out_sent


def check_invalid(in_file, log_file):
	log_file.write('\tDeleting invalid args...\n')
	out_ext = '.check'
	check_file = in_file + out_ext
	
	check_call = 'python ' + args.python_path + 'delete_invalid_args.py -f {0} -out_ext {1}'.format(in_file, out_ext)
	os.system(check_call)
		
	return check_file
		

def get_sent_file(f):
	sent_file = args.sf + f.split('/')[-1].replace(args.prod_ext, args.sent_ext)
	if not os.path.isfile(sent_file):
		raise ValueError("Sent file {0} does not exist".format(sent_file))
	
	return sent_file


def process_dir(f):
	'''Postprocessing AMR folders'''

	log_folder, log_file = get_logs(args.o)
	
	with open(log_file, 'w') as f_out:
		sent_file = get_sent_file(f)
		f_out.write('Processing steps of {0}\n'.format(f))
		print 'Processing steps of {0}\n'.format(f)
		
		file_path = os.path.join(root,f)
		# first do postprocessing steps individually
		
		restore_file, out_sent 		= restore_amr(file_path, f_out, sent_file)
		check_file					= check_invalid(restore_file, f_out)		
		check_file_pruned, out_sent = do_pruning(check_file, f_out, out_sent) 
		coref_file_pruned 			= add_coreference(check_file_pruned, f_out, '.coref.all')
		
		f_out.write('\tDone processing!\n')
		print '\tDone processing!\n'
	
	f_out.close()				

	
if __name__ == "__main__":
	to_do = []
	for root, dirs, files in os.walk(args.o):
		for f in files:
			if f.endswith(args.prod_ext):
				to_do.append(os.path.join(root,f))
	
	
	max_processes = min(len(to_do), 24)
	print 'Processing {0} dirs, {1} in parallel'.format(len(to_do), max_processes)
	
	pool = Pool(processes=max_processes)						
	pool.map(process_dir, to_do)						# process directories in parallel		
				
									
	
	
	
	
	
	

