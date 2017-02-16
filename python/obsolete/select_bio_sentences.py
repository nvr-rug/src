#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
reload(sys)
import argparse
import re
import subprocess
from multiprocessing import Pool

'''Script that selects bio sentences'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with all bio data")
parser.add_argument("-o", required=True, type=str, help="Directory with all bio data")
args = parser.parse_args()


def tokenize(f):
	
	#with open(f,'w') as out_f:
		#for s in sents:
			#out_f.write(s.strip() + '\n')
	#out_f.close()		
	print 'Start tokenizing', f
	
	os.system(u'cat {0} | /net/gsb/gsb/ext/elephant/elephant -m /net/gsb/gsb/ext/elephant/models/english -f iob | sed -e "s/\t/ /" > {0}.tok.iob'.format(f))
	
	print 'IOB done'
	
	# convert to tokenization pivot format (used by various tools to map tokens to offsets etc.)
	os.system('cat {0}.tok.iob | /net/gsb/gsb/src/python/iob2off.py > {0}.tok.off'.format(f))
	
	print 'tok.off done'
	
	# convert to tokenization format used by POS tagger
	os.system('cat {0}.tok.off | /net/gsb/gsb/src/python/off2tok.py > {0}.tok'.format(f))
	
	print 'off2tok done'
	
	# HACK: straighten quotes (not all tools deal with typographical ones)
	os.system("""cat {0}.tok | sed -e "s/[‘’]/'/g" | sed -e 's/[“”]/"/g' > {0}.tok.normalized""".format(f))
	
	print 'normalizing done'

if __name__ == '__main__':
	
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith('.tok.normalized'):
				f_path = os.path.join(root, f)
				all_lines = []
				for line in open(f_path, 'r'):
					if len(line.strip().split()) < 6: 
						if all_lines:
							del all_lines[-1]					# skip line and delete previous one as well because those are usually messed up then
					elif len(line.strip().split()) > 25:	# skip long sentences
						continue
					else:
						all_lines.append(line.strip())
				
				with open(f_path + '.filtered', 'w') as out_f:
					for a in all_lines:
						out_f.write(a.strip() + '\n')
				out_f.close()				
	
	
	#for root, dirs, files in os.walk(args.f):
		#do_files = [os.path.join(root, f) for f in files]
		##print do_files
	#pool = Pool(processes=24)						
	#pool.map(tokenize, do_files)
	
	
	#p = [x.strip() for x in open(args.f,'r')][0]
	#num_files = 0
	#for x in range(0, 36000000, 1500000):
		#part = p[x:x+1500000]
		#output_file = args.o + '_' + str(num_files)
		#num_files += 1
		#split_part = part.split('.')[1:-3]
		#deleted = 0
		#while not split_part[0].strip()[0].isupper():		#remove unfinished sentence in beginning
			#del split_part[0]
		
		#while not split_part[-1].strip()[0].isupper():		#remove unfinished sentence in the end
			#del split_part[-1]
		
		#line = ".".join(split_part)
		
		#with open(output_file,'w') as out_f:
			#out_f.write(line.strip() + '\n')
		#out_f.close()	
	
	#dirs_to_check = os.walk(args.f).next()[1]
	#dirs = [x for x in dirs_to_check if 'cancer' in x.lower()]
	#idx = 0
	#all_lines = 0
	#all_sents = []
	
	#for d in dirs:
		#for root, ds, files in os.walk(args.f + d):
			#for f in files:
				#f_path = os.path.join(root, f)
				#sents = []
				#add_sents = False
				#for l in open(f_path, 'r'):	
					#if l.lower().strip() == 'results':
						#add_sents = True
					#elif not l.strip() and add_sents:
						#break
					#elif add_sents:
						#sents.append(l)
				#if idx % 5000 == 0:
					#print idx
				#idx += 1
				
				#all_sents += sents
				##tokenize('temp.txt',sents)
				
				##if sents and idx % 2000 == 0:
				##	for s in sents:
				##		print s
				##	print 'Idx:', idx
				#all_lines += len(sents)

#with open('all_sents.txt','w') as out_sents:
	#for line in all_sents:
		#if line.split() > 4:
			#out_sents.write(line.strip() + '\n')
#out_sents.close()

#print 'Length all lines', all_lines				
					
