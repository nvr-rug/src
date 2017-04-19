#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script that does individual comparison with 2 AMR files - AMRs should be in one-line format'''

import re,sys, argparse, os, subprocess, json, random
reload(sys)

#python -f1 /home/p266548/Documents/amr_Rik/GMB_data/combined_CAMR_JAMR/part_camr00.txt -f2 /home/p266548/Documents/amr_Rik/GMB_data/combined_CAMR_JAMR/part_jamr00.txt -sent /home/p266548/Documents/amr_Rik/GMB_data/combined_CAMR_JAMR/part_sent00.sent -d /home/p266548/Documents/amr_Rik/GMB_data/combined_CAMR_JAMR/dicts/dict_00.json

parser = argparse.ArgumentParser()
parser.add_argument("-f1", required = True, type=str, help="First file with AMRs")
parser.add_argument("-f2", required = True, type=str, help="Second file with AMRs")
parser.add_argument("-sent", required = True, type=str, help="Sentence file")
parser.add_argument("-d", required = True, type=str, help="Dictionary to save smatch results")
args = parser.parse_args()


def write_to_file(sent, f):
	with open(f,'w') as out_f:
		out_f.write(sent.strip() + '\n')
	out_f.close()	

def do_smatch(amr1, amr2):
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r 4 --both_one_line -f {0} {1}'.format(amr1, amr2)
	
	output = subprocess.check_output(os_call, shell=True)
	f_score = output.split()[-1]
	#print f_score
	return float(f_score)

if __name__ == '__main__':
	
	camr = [x.strip() for x in open(args.f1, 'r') if x]
	jamr = [x.strip() for x in open(args.f2, 'r') if x]
	sents = [x.strip() for x in open(args.sent, 'r') if x]
	assert len(camr) == len(jamr)
	
	if os.path.isfile(args.d):
		print 'Dictionary already exists, do nothing to avoid errors'
	else:
		print 'Start testing'
		res_dict = {}
		for idx in range(len(camr)):
			if sents[idx] not in res_dict:
				rand = str(random.randint(1,100000000))
				f_camr = 'temp_camr_' + rand + '.txt'
				f_jamr = 'temp_jamr_' + rand + '.txt'
				write_to_file(camr[idx], f_camr)
				write_to_file(jamr[idx], f_jamr)
				
				fscore = do_smatch(f_camr, f_jamr)
				
				res_dict[sents[idx]] = [camr[idx], jamr[idx], fscore]
				os.system("rm {0}".format(f_camr))
				os.system("rm {0}".format(f_jamr))
	
		print 'Done testing'
		
		with open(args.d, 'w') as out_f:
			json.dump(res_dict, out_f)
		out_f.close()
