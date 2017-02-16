import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.txt',  required=False, type=str, help="Input extension of AMRs (default .txt")
parser.add_argument("-dict", default = '~/Documents/amr_Rik/no_alignment_dict.txt',  required=False, type=str, help="Dictionary with alignment counts")
args = parser.parse_args()

def add_to_dict(d, key):
	if '~' in key:
		list_item = 1
	else:
		list_item = 0	
	
	key = key.split('~')[0]
	
	if key in d:
		d[key][list_item] += 1 
	else:
		d[key] = [0,0]
		d[key][list_item] += 1
	
	return d	

def process_file(f, d):
	prev_ch = ''
	all_words = []
	
	for line in open(f, 'r'):
		
		if '/' in line:
			new_word = ''
			add_word = False
			
			for ch in line:
				if ch == '/':
					if prev_ch == '/':	#we see a link or something, do not start adding
						add_word = False
					elif add_word:
						add_word = new_word.replace(')','').strip()
						d = add_to_dict(d, add_word)
						new_word = ''
					else:	
						add_word = True
				elif ch == ' ' and prev_ch != '/':
					add_word = False	
				elif add_word:
					new_word += ch
				prev_ch = ch	
			add_word = new_word.replace(')','').strip()
			d = add_to_dict(d, add_word)
	
	return d		
		
			
if __name__ == '__main__':
	d = {}
	
	for root, dirs, files in os.walk(args.f):
		for f in files:
			f_path = os.path.join(root, f)
			d = process_file(f_path, d)
	
	for key in d:
		d[key].append(d[key][0] + d[key][1])
	
	#for idx in range(0,25,25):
	idx = 30
	pct = 0.70
	align, no_align = 0,0
	
	for k, value in sorted(d.items(), key=lambda e: e[1], reverse = True):
		if (float(d[k][2]) * pct) < d[k][0] and d[k][2] > idx:
			no_align += 1
			print k#, d[k]
		else:
			align += 1
	print '{0} out of {1} words have more often no alignment (idx = {2})'.format(no_align, align + no_align, idx)		
							
