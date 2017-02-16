#!/usr/bin/env python
# -*- coding: utf8 -*-

import re,sys, argparse, os, random, collections, subprocess, json
reload(sys)
import validator_seq2seq
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="File with AMRs (one line)")
parser.add_argument("-g", required = True, type=str, help="Gold AMR file with all AMRs")
args = parser.parse_args()


def filter_colons(part):
	'''Funtion to filter out timestamps (e.g. 08:30) and websites (e.g. http://site.com)'''

	new_parts = []
	split_part = part.split(':')
	for idx in range(0, len(split_part)):
		if idx == 0:
			new_parts.append(split_part[idx])
		
		elif split_part[idx][0].isalpha():
			new_parts.append(split_part[idx])
		else:
			new_parts[-1] += ':' + split_part[idx]		# not actually a new part, just add to last one
				
	return new_parts


def most_common(lst):
    return max(set(lst), key=lst.count)


def lookup_best_replacement(name, d):
	if name in d:
		most_common_item = most_common(d[name])
		#print 'Most common arg {0} for name {1} (len {2})'.format(most_common_item, name, len(d[name]))
		return most_common_item
	else:
		return False


def get_word_arg_combos(f):
	word_dict = {}
	digit_rep = 'digit_representation'
	word_dict[digit_rep] = []
	
	for line in open(f, 'r'):
		if not line.startswith('# ::') and line.strip() and ':' in line:
			spl_line = filter_colons(line)
			for idx in range(1, len(spl_line)):	
				arg = spl_line[idx].split()[0].strip()
				search_part = " ".join(spl_line[idx].split()[1:])
				name =  search_part.split(')')[0].split(':')[0]
				if '/' not in name:
					final_name = name.strip()
				else:
					final_name = name.split('/')[-1].strip()
				
				final_name = final_name.replace('"','')

				#print arg, final_name
				
				if final_name not in word_dict:
					word_dict[final_name] = [':' + arg]
				else:
					word_dict[final_name].append(':' + arg)
				
				if final_name.isdigit():
					word_dict[digit_rep].append(':' + arg)
	
	return word_dict				


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_most_freq(word_dict):
	new_l = []
	for key in word_dict:
		new_l += word_dict[key]
	
	c = Counter(new_l)
	most_freq = c.most_common(7)
	best_list = []	
	for m in most_freq:
		best_list.append(m[0])
	
	print best_list
	return best_list

def get_most_freq_digit(word_dict):
	new_l = []
	for key in word_dict:
		if is_number(key):
			new_l += word_dict[key]
	
	c = Counter(new_l)
	most_freq = c.most_common(7)
	best_list = []	
	for m in most_freq:
		best_list.append(m[0])
	
	print best_list
	return best_list	


def remove_both(line):
	#remove null_edge combined with null_tag, stuff like this :null_edge (x2 / null_tag)
	l = re.sub(r':null_edge \([^ ]+ / null_tag\)','', line)
	return_line = " ".join(l.split())
	
	p = re.findall(r':null_edge \([^ ]+ / null_tag\)', line)
	
	return return_line, len(p)


def get_name_from_amr_line(line):
	'''Takes an AMR-line with a :name, returns the full name as a string'''
	name_parts = re.findall(':op[0-9]+ ".*?"', line)
	#name_parts = [x[6:-1] for x in name_parts] # Remove garbage around name parts
	#return ' '.join(name_parts)
	return name_parts[0]
	
def repl_null_edge(f, word_dict, item):
	new_lines = []
	arg_list = []
	replaced = 0
	replace_freq = 0
	total_repl = 0
	
	for line_raw in open(f, 'r'):
		line, num_repl = remove_both(line_raw)
		total_repl += num_repl
		if 'null_edge' in line:
			null_line = line.split(':null_edge')
			keep_str = null_line[0]
			for idx in range(1, len(null_line)):	
				name =  null_line[idx].split(')')[0].split(':')[0]
				if '/' not in name:
					final_name = name.strip()
				else:
					final_name = name.split('/')[-1].strip()
				
				final_name = final_name.replace('"','')
				replaced += 1
				repl = lookup_best_replacement(final_name, word_dict)
				if not repl:
					repl = item
					replace_freq += 1
				keep_str += repl + null_line[idx]
			new_lines.append(keep_str.strip())
		else:
			ok = 1
			new_lines.append(line.strip())
	
	print '\nFor file {0}'.format(f.split('/')[-1])
	print 'Removed {0} double nulledge/nulltag nodes'.format(total_repl)
	print 'Replaced {0} nulledges in total and {1} of those by :name'.format(replaced, replace_freq)
	
	with open(f + '.nonull', 'w') as out_f:
		for l in new_lines:
			out_f.write(l.strip() + '\n')
	out_f.close()				
	
	#os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r 4 --one_line -f ~/Documents/amr_Rik/sem_eval_testdata/ensemble_results/ensemble_test_data.nonull ~/Documents/amr_Rik/bio_data/amrs/test/bio_test_amrs.txt'
	#output = subprocess.check_output(os_call, shell=True)
	#f_score = float(output.split()[-1])
	#print 'F-score {0} = {1}'.format(item, f_score)					

if __name__ == '__main__':
	word_dict = get_word_arg_combos(args.g)
	best_list = get_most_freq(word_dict)
	item = ':name'

	for root, dirs, files in os.walk(args.f):
		for f in files:
			if 'camr' in f and 'nonull' not in f and 'print' not in f and 'wiki' not in f:
				#print f
				f_path = os.path.join(root, f)
				repl_null_edge(f_path, word_dict, item)
	
