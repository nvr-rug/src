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
parser.add_argument('-test', required = True,help="Source test files to be tested")
parser.add_argument('-dev', required = True,help="Source dev files to be tested")
parser.add_argument('-to_process', required = True,help="Process dev or test (accept only dev or test)")
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


def get_logs(output_direc):
	log_folder = "{0}/log".format(output_direc)
	log_file = log_folder + '/' + '/log_testing.txt'
	os.system("mkdir -p {0}".format(log_folder))
	return log_folder, log_file


def process_dir(cp_direc):
	'''Processes a checkpoint directory - producing output for all test files'''

	replace_unk = '-replace_unk' if args.repl else ''	
	gpu = '-gpuid 1' if args.gpu else ''
	direc_name 		= cp_direc.split('/')[-1]
	output_direc 	= args.o + 'output_' + direc_name
	log_folder, log_file = get_logs(output_direc)
	
	os.system('mkdir -p {0}'.format(output_direc))	# create output dir for this checkpoint
	
	if args.to_process == 'dev':
		process_files = args.dev
	elif args.to_process == 'test':
		process_files = args.test
	else:
		print '-to_process must be dev or test'
		sys.exit(0)		
	
	#print process_files
	with open(log_file, 'w') as f_out:
		for root, dirs, files in os.walk(process_files):
			for f in files:
				#print f
				if f.endswith(args.test_ext):
					f_path = os.path.join(root, f)
					out_file = output_direc + '/' + f.replace(args.test_ext,args.prod_ext)
					log_output = log_folder + '/' +  f + '.log'
					
					f_out.write('Starting testing {0}...\n'.format(f))
					print 'Starting testing {0}...'.format(f)
					
					test_call = 'th {0}translate.lua -src {1} -output {2} -model {3} -beam_size {4} -max_sent_length {5} {6} -n_best {7} {8} -log_file {9} -fallback_to_cpu'.format(args.OMT_path, f_path, out_file, args.tf, args.beam_size, args.max_sent_length, replace_unk, args.n_best, gpu, log_output)
					os.system(test_call)	#do python testing with file
					
					f_out.write('Testing complete!\n')
					print 'Testing complete!'
		
	#f_out.close()				
	
if __name__ == "__main__":
	process_dir(args.tf)					
				
									
	
	
	
	
	
	
