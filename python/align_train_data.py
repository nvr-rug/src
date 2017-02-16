#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that aligns multiple AMR and sentence data for the seq2seq model. We want to train om more data, but have
to be dead certain that the right AMR maps to the right sentence'''

parser = argparse.ArgumentParser()
parser.add_argument("-a", required=True, type=str, help="folder with the to be combined AMRs")
parser.add_argument('-s', required = True,type=str, help="folder with the to be combined sentences")
parser.add_argument('-o', required = True,type=str, help="outfile")
parser.add_argument('-char_input_ext', required = True,type=str, help="Input extension for character-level files")
parser.add_argument('-char_output_ext', required = True,type=str, help="Output extension for character-level files")

args = parser.parse_args()

def create_output(amrs, sents, log):
	with open('{0}{1}'.format(args.o, args.char_output_ext),'w') as f:
		for l in amrs:
			f.write(l + '\n')
	f.close()
	
	with open('{0}{1}'.format(args.o, args.char_input_ext),'w') as f:
		for l in sents:
			f.write(l + '\n')
	f.close()
	
	with open('{0}.log'.format(args.o),'w') as f:
		f.write('Log file for adding AMR and sentence files\n\n')
		f.write('Folder with AMRs: {0}\nFolder with sentences: {1}\n\nFolder with output: {2}\n\nOrder:\n'.format(args.a, args.s, args.o))
		for l in log:
			f.write(l[0] + ' ' + l[1] + '\n')
	f.close()
			

if __name__ == "__main__":
	all_amrs = []
	all_sent = []
	log = []
	
	for root_a, dirs_a,files_a in os.walk(args.a):
		for fname_a in files_a:
			for root_s, dirs_s, files_s in os.walk(args.s):
				for fname_s in files_s:
					if fname_a.split('.')[0] == fname_s.split('.')[0] and args.char_output_ext in fname_a and args.char_input_ext in fname_s:		# check if same file:
						log.append([fname_a, fname_s])
						a_path = os.path.join(root_a,fname_a)
						s_path = os.path.join(root_s,fname_s)
						print fname_a
						print 'len',len([x.strip() for x in open(a_path,'r')]),'\n'
						all_amrs += [x.strip() for x in open(a_path,'r')]
						all_sent += [x.strip() for x in open(s_path,'r')]
	
	create_output(all_amrs, all_sent, log)					
