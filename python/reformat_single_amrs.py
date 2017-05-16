#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script that reformats AMRs back to their original format with tabs and enters'''

import sys,re,argparse, os

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="file with the to be formatted AMRs")
#parser.add_argument("-sf", required=True, type=str, help="file with the to be formatted sentences")
#parser.add_argument('-o',type=str, help="output-folder for reformatted AMRs")
args = parser.parse_args()

def process_file(f):
	fixed_amrs = []
	prev_ch = ''
	sents = [x.strip() for x in open('/home/p266548/Documents/amr_Rik/Exp_OMT/Combinations/data_files/training_aligned/silver_camr_jamr_AMR_constant_100k.sent','r')]
	for idx, line in enumerate(open(f,'r')):
		num_tabs = 0
		amr_string = '# ::snt ' + sents[idx] + '\n'
		for ch in line:
			if ch == '(':
				num_tabs += 1
				amr_string += ch
			elif ch == ')':
				num_tabs -= 1
				amr_string += ch
			elif ch	 == ':':	
				if prev_ch == ' ':	#only do when prev char is a space, else it was probably a HTML link or something
					amr_string += '\n' + num_tabs * '\t' + ch
				else:
					amr_string += ch	
			else:
				amr_string += ch
			prev_ch = ch
				
		amr_string += '\n'
		fixed_amrs.append(amr_string)
			
	return fixed_amrs	

if __name__ == "__main__":
	fixed_amrs = process_file(args.f)
	with open(args.f + '.print', 'w') as out_f:
		for amr in fixed_amrs:
			out_f.write(amr.strip() + '\n\n')
	out_f.close()	
	
	#for root, dirs, files in os.walk(args.f):
		#for f in files:
			#if f.endswith('.nonull') or 'seq' in f:
				#f_path = os.path.join(root, f)
				#print f_path
				#fixed_amrs = process_file(f_path)
				#with open(f_path + '.print', 'w') as out_f:
					#for amr in fixed_amrs:
						#out_f.write(amr.strip() + '\n\n')
				#out_f.close()		
	
	
	
	
	#sents = [x.strip() for x in open(args.sf, 'r')]
	#assert(len(sents) == len(fixed_amrs))
	
	#count = 0
	#for sent, amr in zip(sents, fixed_amrs):
	#	count += 1
	#	print '# ::snt{0} {1}'.format(count, sent)
	#	print amr.strip(),'\n'
