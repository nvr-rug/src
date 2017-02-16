#!/usr/bin/env python
# -*- coding: utf8 -*-

import re,sys, argparse, os, random, collections, subprocess, json
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="File with AMRs (one line)")
parser.add_argument("-d", default = '/home/p266548/Documents/amr_Rik/sem_eval_testdata/wiki_dict.txt', type=str, help="wiki dict")
args = parser.parse_args()


def get_name_from_amr_line(line):
	'''Takes an AMR-line with a :name, returns the full name as a string'''
	name_parts = re.findall(':op[0-9]+ ".*?"', line)
	name_parts = [x[6:-1] for x in name_parts] # Remove garbage around name parts
	return ' '.join(name_parts)



if __name__ == '__main__':
	with open(args.d,'r') as in_f:
		wiki_dict = json.load(in_f)
	
	all_lines = []
	errors = 0
	found_wiki = 0
	
	amrs = []
	cur_amr = []
	
	for line in open(args.f, 'r'):
		if not line.strip():
			amrs.append(" ".join(cur_amr))
			cur_amr = []
		else:
			cur_amr.append(line.strip())
		
			
	for idx, line in enumerate(amrs):
		name_split = line.split(':name')
		found = False
		for name_idx in range(1, len(name_split)):	  # skip first in split because name did not occur there yet
			name = get_name_from_amr_line(name_split[name_idx])
			if name in wiki_dict:
				try:	
					name_split[name_idx-1] += ':wiki "' + wiki_dict[name] + '" '
					found_wiki += 1
					found = True
					print 'name: {1} wiki: {2}'.format(idx, name, wiki_dict[name])
				except:
					print line
					print name,'\n'
					pass

		try:
			wikified_line = ":name".join(name_split).strip().encode('utf-8')
		except:
			wikified_line = line
			if found:
				errors += 1
		all_lines.append(wikified_line)		
			
	print 'Inserted Wiki link {0} times, errors {1}'.format(found_wiki, errors)			
	
	with open(args.f + '.wiki', 'w') as out_f:
		for l in all_lines:
			out_f.write(l.strip() + '\n')
	out_f.close()		
					
		#try:
		#	wikified_line = ":name".join(name_split).strip().encode('utf-8')
		#except:	#unicode error
		#	unicode_errors += 1
		#	wikified_line = line.strip()
