import os
import sys
import argparse
import time

'''Script that checks what POS tags do not usually have an alignment in the AMR'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory that contains aligned AMRs")
parser.add_argument("-p", required=True, type=str, help="Directory with files with postagged sentences")
parser.add_argument("-pos_ext", default = '.sent.pos', type=str, help="POS extension")
parser.add_argument("-amr_ext", default = '.txt', type=str, help="AMR extension")
args = parser.parse_args()

def single_line_amrs(amr_lines):
	new_l = ''
	amrs = []
	for line in amr_lines:
		if not line.strip():
			amrs.append(new_l.strip())
			new_l = ''
		elif not line.startswith('# ::	'):
			new_l += ' ' + line
	
	if new_l:
		amrs.append(new_l.strip())
	
	return amrs[1:]		#first "AMR" needs to be skipped here (general information)		


def get_align_nums(amrs):
	
	align_nums = []
	
	for amr in amrs:
		nums = []
		for w in amr.split():
			if '~' in w:
				num = w.split('~')[-1].split('.')[-1].replace(')','')
				if ',' in num:
					multiple = num.split(',')
					nums += multiple
				else:
					nums.append(num)
						
		align_nums.append([int (n) for n in nums if n.isdigit()])	
	
	return align_nums
	

def pos_alignment(align_nums, sents, pos_dict):
	
	for nums, sent in zip(align_nums, sents):
		for idx, word in enumerate(sent.split()):
			if '|' in word:
				pos_tag = word.split('|')[-1]
				
				if idx in nums:			#word has an alignment
					if pos_tag in pos_dict:
						pos_dict[pos_tag][0] += 1
					else:
						pos_dict[pos_tag] = [1,0]	
				else:
					if pos_tag in pos_dict:
						pos_dict[pos_tag][1] += 1
					else:
						pos_dict[pos_tag] = [0,1]
	
	return pos_dict					

if __name__ == '__main__':
	pos_dict = {}
	
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.amr_ext):
				ident = f.split('-')[-1].replace(args.amr_ext,'')
				amr_file = os.path.join(root, f)
				for root2, dirs2, files2, in os.walk(args.p):
					for f2 in files2:
						if ident in f2 and f2.endswith(args.pos_ext) and 'char' not in f2:		#match
							sent_file = os.path.join(root2, f2)
							
							sents = [x.strip() for x in open(sent_file, 'r')]
							amr_lines = [x.strip() for x in open(amr_file, 'r')]
							amrs = single_line_amrs(amr_lines)
							align_nums = get_align_nums(amrs)
							
							assert(len(amrs) == len(sents) == len(align_nums))
							pos_dict = pos_alignment(align_nums, sents, pos_dict)
	
	pos_dict2 = {}
	
	for key in pos_dict:
		pos_dict2[key] = round(float(pos_dict[key][1]) / float(pos_dict[key][0] + pos_dict[key][1]) * 100,1)
	
	for key in sorted(pos_dict2, key = pos_dict2.get,  reverse = True):
		if pos_dict[key][0] + pos_dict[key][1] > 100:
			print '|', key
			print '|', pos_dict[key][0]
			print '|', pos_dict[key][1]
			print '|', str(pos_dict2[key]) + '%'
			print '|-'							
