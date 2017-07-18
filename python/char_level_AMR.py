#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Scripts that sets input files in char-level 
   Possible to keep structure words as single "char", e.g. :domain, :ARG1, :mod, etc'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-sent_ext", default = '.sent',  required=False, type=str, help="Input extension of AMRs (default .sent)")
parser.add_argument("-amr_ext", default = '.tf', required=False, type=str, help="Output extension of AMRs (default .tf)")
parser.add_argument('-words', action='store_true', help='Adding word-level input')
parser.add_argument('-s', action='store_true', help='Adding super characters for AMR files')
parser.add_argument('-c', action='store_true', help='If there is path-coreference in the input')
parser.add_argument('-pos', action='store_true', help='Whether input is POS-tagged')
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f, 'w') as out:
		for l in lst:
			out.write(l.strip() + '\n')
	out.close()


def get_fixed_lines(file_lines):
	'''Fix lines, filter out non-relation and put back coreference paths'''
	
	fixed_lines = []
				
	for line in file_lines:
		spl = line.split()
		for idx, item in enumerate(spl):
			if len(item) > 1 and item[0] == ':':
				if any(x in item for x in [')','<',')','>','/','jwf9X']):		#filter out non-structure words, due to links etc
					new_str = ''
					for ch in item:
						new_str += ch + ' '
					spl[idx] = new_str.strip()
		fixed_lines.append(" ".join(spl))
	
	### Step that is coreference-specific: change | 1 | to |1|, as to not treat the indexes as normal numbers, but as separate super characters
	
	if args.c:
		new_lines = []
		for l in fixed_lines:
			new_l = re.sub(r'\| (\d) \|',r'|\1|', l)
			new_lines.append(new_l)
		return new_lines	
	else:		
			
		return fixed_lines


def get_amr_lines(f_path):
	file_lines = []
	for line in open(f_path,'r'):
		line = line.replace(' ','+') #replace actual spaces with '+'
		new_l = ''
		add_space = True
		for idx, ch in enumerate(line):
			
			if ch == ':' and line[idx+1].isalpha():		#after ':' there should always be a letter, otherwise it is some URL probably and we just continue
				add_space = False
				new_l += ' ' + ch
			elif ch == '+':
				add_space = True
				new_l += ' ' + ch
			else:
				if add_space:
					new_l += ' ' + ch
				else:					#we previously saw a ':', so we do not add spaces
					new_l += ch	
		file_lines.append(new_l)
	
	return file_lines


def process_word_level(f, out_f):
	new_lines = []
	for line in open(f, 'r'):
		split_l = line.replace(')',' ) ').replace('(',' ( ').replace('"',' " ').replace("'"," ' ").split()
		new_split = []
		for l in split_l:
			if '-' in l and 'http' not in l and 'www' not in l and l.count('-') == 1:	#find words with dashes but don't do websites
				l = l.replace('-',' -').split()
				for item in l:
					new_split.append(item)
			else:
				new_split.append(l)
		
		new_l = " ".join(new_split)
		new_lines.append(new_l)
	
	write_to_file(new_lines, out_f)


def process_pos_tagged(f_path):
	fixed_lines = []
	
	
	for line in open(f_path, 'r'):
		new_l = ''
		no_spaces = False
		line = line.replace(' ','+') #replace actual spaces with '+'
		
		for idx, ch in enumerate(line):
			if ch == '|':
				no_spaces = True	#skip identifier '|' in the data
				new_l += ' '
			elif ch == ':' and line[idx-1] == '|':	#structure words are also chunks
				no_spaces = True
			elif ch == '+':
				no_spaces = False
				new_l += ' ' + ch
			elif no_spaces: #and (ch.isupper() or ch == '$'):		#only do no space when uppercase letters (VBZ, NNP, etc), special case PRP$	(not necessary)
				new_l += ch
			else:
				new_l += ' ' + ch
		fixed_lines.append(new_l)
	
	return fixed_lines


def word_level_sent(f, out_f):
	'''Put sentences in word-level input
	   If errors: run this: export PATH=/net/gsb/gsb/ext/elephant:/net/gsb/gsb/ext/elephant/ext:$PATH
	   Do this on sentence level, because Elephant also creates new sentences, which is obviously not wanted'''
	
	sents = []
	
	for idx, s in enumerate(open(f, 'r')):
		if idx % 100 == 0:
			print idx
		
		with open('temp.toktmp','w') as tmp:
			tmp.write(s.strip())
		tmp.close()	
		
		os.system("cat temp.toktmp | /net/gsb/gsb/ext/elephant/elephant -m /net/gsb/gsb/ext/elephant/models/english/ -f iob | sed -e 's/\t/ /'  > temp.tok.iob".format(s))
		os.system("cat temp.tok.iob | ~/Documents/pmb_lc/src/python/iob2off.py > temp.tok.off")
		os.system("cat temp.tok.off | /net/gsb/pmb/src/python/off2tok.py > temp.tok")
		
		new_sent = " ".join([x.strip() for x in open('temp.tok','r')])
		sents.append(new_sent)

		os.system("rm temp.tok*".format(f))	#remove temp files
	
	write_to_file(sents, out_f)	
		
	   
		
if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:							
			if  '.char' not in f:					#already processed this file
				f_path = os.path.join(root, f)		
				if f.endswith(args.amr_ext):				
					out_f =  f_path.replace(args.amr_ext, '.char' + args.amr_ext)
					
					if args.words:
						print 'AMR file, word-level input'
						process_word_level(f_path, out_f)
						
					elif args.s:						#add super characters
						print 'AMR file, super characters'
						amr_lines  = get_amr_lines(f_path)
						fixed_lines = get_fixed_lines(amr_lines)
						write_to_file(fixed_lines, out_f)
					else:
						print 'AMR file, no super characters'
						os_call =  'sed -e "s/\ /+/g"  -e "s/./&\ /g" < {0} > {1}'.format(f_path, out_f)
						os.system(os_call)
				
				elif f.endswith(args.sent_ext):					#different approach for pos-tagged sentences
					out_f =  f_path.replace(args.sent_ext,'.char' + args.sent_ext)
					
					if args.words:
						print 'Sentence file, word-level input'
						word_level_sent(f_path, out_f)
						
					elif args.pos:
						print 'Sentence file, POS-tagged'
						lines = process_pos_tagged(f_path)
						write_to_file(lines, out_f)
					else:
						print 'Sentence file, not POS-tagged'	#do normal char-level approach for sentence files
						os_call =  'sed -e "s/\ /+/g"  -e "s/./&\ /g" < {0} > {1}'.format(f_path, f_path.replace(args.sent_ext,'.char' + args.sent_ext))
						os.system(os_call)
