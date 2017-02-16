import sys
import re
import argparse
import os
import shlex
import subprocess
import validator_seq2seq
import wikification_seq2seq
'''Script that tests given seq2seq model on given test data - with converting produced AMRs'''

# python test_seq2seq_model.py -f ~/Documents/amr_Rik/data_2017/data/amrs/split/test_char -df data_test_23sep -tf checkpoint_test_23sep -sf output_2lay_256s_69k/test -size 256 -layers 2
# python test_seq2seq_model.py -f ~/Documents/amr_Rik/data_2017/data/amrs/split/test_char -df data_test_28sep_s400_l1_batch12_24k -tf checkpoint_test_28sep_s400_l1_batch12_24k -sf output_1lay_400s_24k/test -size 400 -layers 1
# python test_seq2seq_model.py -f ~/Documents/amr_Rik/data_2017/data/amrs/split/test_char -df data_test_28sep_s400_l1_batch12_50k -tf checkpoint_test_28sep_s400_l1_batch12_50k -sf output_1lay_400s_50k/test -size 400 -layers 1
# python test_seq2seq_model.py -f ~/Documents/amr_Rik/data_2017/data/amrs/split/test_char -df data_test_28sep_s400_l1_batch12_111k -tf checkpoint_test_28sep_s400_l1_batch12_111k -sf output_1lay_400s_111k/test -size 400 -layers 1

#python test_seq2seq_model.py -f ~/Documents/amr_Rik/data_2017/data/amrs/split/test_char -df data/s400_l1_batch12_150k -tf checkpoints/s400_l1_batch12_150k -sf output/1lay_400s_150k/test -size 400 -layers 1
#python test_seq2seq_model.py -f ~/Documents/amr_Rik/data_2017/data/amrs/split/test_char -df data/s400_l1_batch12_205k -tf checkpoints/s400_l1_batch12_205k -sf output/1lay_400s_205k/test -size 400 -layers 1

#python test_seq2seq_model.py -f ~/Documents/amr_Rik/Seq2seq/working_old/test_char -df data/data_old/old_s400_l1_batch10 -tf checkpoints/checkpoints_old/old_s400_l1_batch10_400k -sf output/output_old/s400_l1_batch10_400k/test -size 400 -layers 1
#python test_seq2seq_model.py -f ~/Documents/amr_Rik/Seq2seq/working_old/test_char -df data/data_old/old_s400_l1_batch10 -tf checkpoints/checkpoints_old/old_s400_l1_batch10_450k -sf output/output_old/s400_l1_batch10_450k/test -size 400 -layers 1
#python test_seq2seq_model.py -f ~/Documents/amr_Rik/Seq2seq/working_old/test_char -df data/data_old/old_s400_l1_batch10 -tf checkpoints/checkpoints_old/old_s400_l1_batch10_500k -sf output/output_old/s400_l1_batch10_500k/test -size 400 -layers 1
#python test_seq2seq_model.py -f ~/Documents/amr_Rik/Seq2seq/working_old/test_char -df data/data_old/old_s400_l1_batch10 -tf checkpoints/checkpoints_old/old_s400_l1_batch10_550k -sf output/output_old/s400_l1_batch10_550k/test -size 400 -layers 1
#python test_seq2seq_model.py -f ~/Documents/amr_Rik/Seq2seq/working_old/test_char -df data/data_old/old_s400_l1_batch10 -tf checkpoints/checkpoints_old/old_s400_l1_batch10_600k -sf output/output_old/s400_l1_batch10_600k/test -size 400 -layers 1

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="folder that contains to be processed files (dev or test)")
parser.add_argument('-df', required = True,help="data folder for seq2seq model")
parser.add_argument('-tf', required = True,help="test folder for seq2seq model (actual model)")
parser.add_argument('-sf', required = True,help="Folder where we save all our output")
parser.add_argument('-size',default = 400, type = int ,help="size of model")
parser.add_argument('-layers',default = 1, type = int ,help="number of layers in model")
parser.add_argument('-no_rewrite',default = False, type = bool ,help="number of layers in model")
args = parser.parse_args() 

def write_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	
	return default

def check_valid(restore_file, rewrite):
	idx = 0
	warnings = 0
	all_amrs = []
	for line in open(restore_file,'r'):
		idx += 1
		if not validator_seq2seq.valid_amr(line):
			print 'Error or warning in line {0}, write default'.format(idx)
			warnings += 1
			default_amr = write_default_amr()
			all_amrs.append(default_amr)		## add default when error
		else:
			all_amrs.append(line)	
	
	if warnings == 0:
		print '\t\tNo badly formed AMRs!'
	elif rewrite:
		print '\t\tRewriting {0} AMRs with error to default AMR'.format(warnings)
		
		with open(restore_file,'w') as out_f:
			for line in all_amrs:
				out_f.write(line.strip()+'\n')
	else:
		print '\t\t{0} AMRs with warning - no rewriting to default'.format(warnings)	
						

if __name__ == "__main__":
	os.system('mkdir -p {0}'.format(args.sf))	#create output dir
	
	print '\nStarting test procedure...'
	test_call = 'python translate_decode_file.py --multiple_files --test_folder {5} --out_folder {4} --decode --data_dir {0} --train_dir {1} --size={2} --num_layers={3}'.format(args.df, args.tf, args.size, args.layers, args.sf, args.f)
	print test_call
	os.system(test_call)	#do python testing with file
	print 'Testing complete!'
	
	for root, dirs, files in os.walk(args.sf):
		for f in files:
			if f.endswith('.seq.amr'):
				print 'Processing {0}'.format(f)
				file_path = os.path.join(root,f)
				print '\tRestoring...'
				restore_file = args.sf + '/' + f + '.restore'
				restore_call = 'python restoreAMR/restore_amr.py {0} > {1}'.format(file_path, restore_file)
				os.system(restore_call)
				print '\tValidating...'
				check_valid(restore_file, True)
				
				sent_file = args.f.replace('_char','/') + f.replace('.seq.amr','.sent')
				print '\tDoing Wikification...'
				wikification_seq2seq.wikify_pipeline_output(restore_file, 'dbpedia', sent_file)
				print '\tValidating again...'
				check_valid(restore_file + '.wiki', False)
				print '\tDone processing!\n'
				
					
				
					
									
	
	
	
	
	
	
