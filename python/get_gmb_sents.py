#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
import utils


'''Scripts for obtaining GMB data'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Starting directory")
args = parser.parse_args()

def get_sents(f):

	empty = True
	old_snum = 1
	final_string = ''
	
	for line in open(f,'r'):
		line = line.strip()
		if line:
			empty = False
			fields = line.split(' ', 3)
			snum = int(fields[2][:-3]) # sentence number
			tnum = int(fields[2][-3:]) # token number
			# if token is an empty string
			if len(fields) == 3:
				fields.append('')
			token = fields[3]
			if snum != old_snum:
				final_string += '\n' # sentence boundary
				old_snum = snum
			elif tnum != 1:
				final_string += ' ' # token boundary
			final_string += token	

	if not empty:
		final_string += '\n' # newline to end last sentence
	
	return final_string.split('\n')	

if __name__ == '__main__':
	all_sents = []
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f == 'en.tok.off':
				f_path = os.path.join(root,f)
				all_sents += get_sents(f_path)
	
	all_sents_fil = [x for x in all_sents if x]
	print 'Length all sents: {0}'.format(len(all_sents_fil))
	
	with open('/home/p266548/Documents/amr_Rik/GMB_data/all_gmb.txt','w') as out_f:
		for s in all_sents_fil:
			out_f.write(s.strip() + '\n')
	out_f.close()		
