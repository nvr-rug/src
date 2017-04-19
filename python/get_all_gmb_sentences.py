#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Obtain all Voice of America GMB sentences, uncategorized'''

import re,sys, argparse, os, subprocess, json
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="Starting folder")
parser.add_argument("-o", required = True, type=str, help="Save sentences to this file")
args = parser.parse_args()

def filter_lines(lines):
	'''Filter lines found in corpus, no weird character of strange quotes'''
	
	lines = [x.replace('“','"').replace('”','"').replace('[','(').replace(']',')').replace('`',"'").replace('_',' ').replace('|',' ').replace('~',' ').replace('{','(').replace('}',')') for x in lines]
	lines = [" ".join(x.split()) for x in lines] #remove double spaces
	new_data = []
	
	for line in lines:
		if '>' not in line and '<' not in line and '=' not in line:
			if line and (line[0].isalpha() or line[0] == '"'):
				if len(line.split()) > 4:
					if line.startswith('" ') and line.count('"') % 2 != 0:
						new_line = line[2:]
					elif line.endswith(' "') and line.count('"') % 2 != 0:
						new_line = line[:-2]
					elif line.count('"') == 1:
						new_line = " ".join(line.replace('"',' ').split())
					else:
						new_line = line
					
					new_data.append(new_line)
	return new_data				


if __name__ == '__main__':
	#new_data = []
	#idx = 0
	#for root, dirs, files in os.walk(args.f):
		#if 'en.raw' in files and 'en.met' in files:
			#if 'Voice of America' in open(os.path.join(root, 'en.met')).read():
				#tok_path = '/net/gsb/gsb/out/' + "/".join(root.split('/')[5:]) + '/' + 'en.tok'
				#idx += 1
				#if os.path.isfile(tok_path):
					#new_data += [x.strip() for x in open(tok_path) if x]
					##with open(args.o,'w') as out_f:
					##	for n in new_data:
					##		out_f.write(n.strip().replace('␣',' ') + '\n')
					##out_f.close()
					
	
	#with open(args.o,'w') as out_f:
		#for n in new_data:
			#out_f.write(n.strip().replace('␣',' ') + '\n')
	#out_f.close()		
	
	lines = [x.strip() for x in open(args.o,'r')]
	new_data = filter_lines(lines)		
	
	all_chars = {}
	
	#for line in new_data:
	#	for ch in line:
	#		print ch
	
					
	
	print len(new_data)
	
	with open(args.o + '.fil','w') as out_f:
		for n in new_data:
			out_f.write(n.strip().replace('␣',' ') + '\n')
	out_f.close()	
