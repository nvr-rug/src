#!/usr/bin/env python
# -*- coding: utf8 -*-

import re,sys, argparse, os, random
reload(sys)
import validator_seq2seq

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="Folder with output files")
parser.add_argument("-ext", default = '.seq.amr', type=str, help="Extension of file that need to be processed")

args = parser.parse_args()

def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()		


def get_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	return default


def restore_AMR(in_f):
	out_f = in_f + '.restore'
	os_call = 'python restoreAMR/restore_amr.py {0} > {1}'.format(in_f, out_f)
	os.system(os_call)
	return out_f


def get_temp_file(lines_temp, f_path):
	'''Put in such a format that restoring still works'''
	
	new_lines = []
	lines = [x.replace('}',' } ').replace('{',' { ') for x in lines_temp]
	
	for line in lines:		
		if '{' in line:
			line_parts = []
			coref_parts = []
			coref = False
			for item in line.split():				
				if item == '{':
					line_parts.append('(')	#add brackets
					coref = True
				elif item == '}':
					add_part = 'COREF*' + "*".join(coref_parts).replace(':','COLON')
					line_parts.append(add_part)
					line_parts.append(')')
					coref = False
					coref_parts = []
				elif coref:
					coref_parts.append(item)
				else:
					line_parts.append(item)
			new_lines.append(" ".join(line_parts))			
							
		else:
			new_lines.append(line)  #no coreference here, do nothing
	out_file = f_path + '.temp'
	write_to_file(new_lines, out_file)
	
	return out_file


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


def tokenize_line(line):
	new_l = line.replace('(', ' ( ').replace(')',' ) ')
	return " ".join(new_l.split())


def tokenize_file(f):
	new_lines = []
	for line in open(f, 'r'):
		new_l = tokenize_line(line)
		new_lines.append(new_l)
	return new_lines	


def get_permutations(search_part):
	'''Get the initial permutations and add_string'''
	
	paren_count = 0
	start_adding = False
	permutations = []	
	add_string = ''
	
	for idx, ch in enumerate(search_part):
		if ch == '(':					# parenthesis found
			if start_adding:
				add_string += ch
			paren_count += 1
		elif ch == ':':
			start_adding = True
			add_string += ch
		elif ch == ')':
			paren_count -= 1
			if start_adding:
				add_string += ch
			if paren_count == 0:		# we closed one of the permutations now
				permutations.append(add_string.strip())
				add_string = ''
		elif start_adding:
			add_string += ch				
	
	if add_string and ':' in add_string:
		permutations.append(add_string.replace(')','').strip())
		for idx, p in enumerate(permutations):
			while permutations[idx].count(')') < permutations[idx].count('('):
				permutations[idx] += ')'
	
	#permutate without brackets (e.g. :op1 "hoi" :op2 "hai" :op3 "ok"	
	for p in permutations:
		if ')' not in p or '(' not in p:				
			if p.count(':') > 2:
				p_split = p.split(':')[1:]
				new_perms = [':' + x.strip() for x in p_split]
				return add_string, new_perms
	
	return permutations		


def get_keep_string(new_parts, level):
	'''Obtain string we keep, it differs for level 0'''
	
	if level > 0:
		keep_string = ':' + ":".join(new_parts[:1])
	else:
		keep_string = ":".join(new_parts[:1])
	search_part = ':' + ":".join(new_parts[1:])
	
	return keep_string, search_part


def get_reference(search_part):
	spl_line = search_part.split()
	for idx in range(len(spl_line)):
		if spl_line[idx] == '/':
			ref_var = spl_line[idx-1]
			break
			
	return ref_var		


def matching_perm(permutations, rel, count):
	num_matches = 0
	matching_perm = ''
	
	for p in permutations:
		rel_p = p.split()[0]
		if rel_p == rel:
			num_matches += 1
			if num_matches == count:
				matching_perm = p
				#print 'Found match, {0} and {1}'.format(rel_p, rel)
	return matching_perm


def get_random_var(line):
	variables = re.findall(r'\( ([a-zA-Z0-9-_]+) \/', line)
	var_list = [x for x in variables if 'COREF' not in x]
	return random.choice(var_list)


def get_closest_var(permutations):
	all_vars = []
	for p in permutations:
		v = re.findall(r'\( ([a-zA-Z0-9-_]+) \/', p)
		all_vars += v
	
	var_list = [x for x in all_vars if 'COREF' not in x]
	return random.choice(var_list)	


def find_replacement(line, item):
	path = item.replace('COREF','').replace('COLON',':').replace('*',' ').strip()
	args = [x for idx, x in enumerate(path.split()) if idx % 2 == 0]
	num =  [x for idx, x in enumerate(path.split()) if idx % 2 != 0]
	nums = [int(x.replace('|','').strip()) for x in num]
	
	tok_line = tokenize_line(line)
	new_parts = filter_colons(tok_line)												#remove non-arguments that have a colon such as timestamps and websites
	keep_string, search_part = get_keep_string(new_parts, 0)
	path_found = True
	
	print args
	
	for idx in range(0, len(args)):
		permutations = get_permutations(search_part)	
		search_part = matching_perm(permutations, args[idx], nums[idx])
		
		if not search_part:
			closest_var = get_closest_var(permutations)
			path_found = False
			break # no path found
	
	print 'Total'
	
	if path_found:
		ref_var = get_reference(search_part)
		print 'Found'
		return ref_var
	else:
		print 'Not found'
		random_var = get_random_var(line)
		#print closest_var
		return closest_var
		#return ''			#delete node
		#return random_var	#random
		

def replace_coref(f):
	lines = tokenize_file(f)
	new_lines = []
	for line in lines:
		spl_line = line.split()
		new_line = line
		for idx, item in enumerate(spl_line):
			if 'COREF*' in item:
				repl = find_replacement(line, item)					#find actual replacement here
				if repl:
					to_be_replaced = " ".join(spl_line[idx-3:idx+2])	#replace this part with the reference
				else:
					to_be_replaced = " ".join(spl_line[idx-4:idx+2])	#remove reference, so also include the argument
				
				if to_be_replaced not in new_line:						#do the replacement
					print 'Something is wrong here'
				else:
					new_line = new_line.replace(to_be_replaced, repl)	
		
		while ' )' in new_line or '( ' in new_line:					#restore tokenizing
			new_line = new_line.replace(' )',')').replace('( ','(')
		
		if validator_seq2seq.valid_amr(new_line):
			new_lines.append(new_line)
		else:
			ep = re.findall(r'epoch([\d]+)',f)
			print 'Invalid AMR, writing default AMR, epoch: {0}'.format(ep[0])
			default_amr = get_default_amr()
			new_lines.append(default_amr)

	write_to_file(new_lines, f.replace('.temp','') + '.coref')				
		

if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.ext):
				f_path = os.path.join(root, f)
				lines = [x.replace(' ','').replace('+',' ').strip() for x in open (f_path, 'r')]
				temp_file	 = get_temp_file(lines, f_path)
				restore_file = restore_AMR(temp_file)
				replace_coref(restore_file)	
				
				#os_call = 'rm {0}/*temp*'.format(root)
				#os.system(os_call)	#clean up temp files		
