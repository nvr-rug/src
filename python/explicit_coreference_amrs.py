#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that converts the AMRs to a single line, taking care of re-entrancies in a nice way
   It does this by adding the absolute or relative paths'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains the amrs")
parser.add_argument('-extension', required = False, default = '.txt', help="extension of AMR files (default .txt)")
parser.add_argument('-output_ext', required = False, default = '.tf', help="extension of output AMR files (default .tf)")
parser.add_argument('-p', required = True, action='store', choices=['rel','abs'], help='Add relative or absolute path?')
args = parser.parse_args()


def single_line_convert(amrs):
	single_amrs = []
	cur_amr = []
	sents = []
	
	for line in amrs:
		if not line.strip() and cur_amr:
			single_amrs.append(" ".join(cur_amr))
			cur_amr = []
		elif line.startswith('#'):
			if line.startswith('# ::snt'):
				sents.append(line.replace('# ::snt','').strip())
		else:
			cur_amr.append(line.strip())					
	assert(len(single_amrs) == len(sents))
	
	return single_amrs, sents


def delete_wiki(f):
	no_wiki = []
	for line in open(f, 'r'):
		n_line = re.sub(r':wiki "(.*?)"', '', line, 1)
		n_line = re.sub(':wiki -', '', n_line)
		no_wiki.append((len(n_line) - len(n_line.lstrip())) * ' ' + ' '.join(n_line.split()))  # convert double whitespace but keep leading whitespace
	return no_wiki


def process_var_line(line, var_dict):
	'''Function that processes line with a variable in it. Returns the string without 
	   variables and the dictionary with var-name + var - value'''
	curr_var_name = False
	curr_var_value = False
	var_value = ''
	var_name = ''
	for idx, ch in enumerate(line):
		if ch == '/':				# we start adding the variable value
			curr_var_value = True
			curr_var_name = False
			var_value = ''
			continue
		
		if ch == '(':				# we start adding the variable name										
			curr_var_name = True
			curr_var_value = False
			if var_value and var_name:		#we already found a name-value pair, add it now
				var_dict[var_name.strip()] = var_value.strip().replace(')','').replace(' :name','').replace(' :dayperiod','').replace(' :mod','')
			var_name = ''
			continue	
		
		if curr_var_name:		# add to variable name
			var_name += ch
		if curr_var_value:		# add to variable value
			var_value += ch
	
	var_dict[var_name.strip()] = var_value.strip().replace(')','')					
	deleted_var_string = re.sub(r'\((.*?/)', '(', line).replace('( ', '(')					# delete variables from line
	
	return deleted_var_string, var_dict


def get_var_dict(spl):
	'''Function that returns a dictionary with all variable and their absolute path for an AMR'''
	
	cur_path = []
	level = 0
	all_paths = []
	var_dict = dict()
	previous_open = False
	previous_close = False
	
	for idx in range(1, len(spl)):	#skip first parenthesis
		if spl[idx] == '(':
			level += 1
			cur_path, all_paths = find_cur_path_addition(cur_path, spl, idx, all_paths)
			previous_close = False
		
		elif spl[idx] == ')':
			level -= 1
			previous_close = True
		
		elif spl[idx] == '/':
			var_name  = spl[idx-1]				#var found
			var_value =	spl[idx+1]
			if var_name not in var_dict:
				var_dict[var_name] = [var_value, " ".join(cur_path)]
			previous_close = False
		
		elif previous_close:		
			cur_path = cur_path[0:level]
			previous_close = False
		
		else:
			previous_close = False
	
	return var_dict		


def variable_match(spl, idx, no_var_list, vars_seen):
	'''Function that matches entities that are variables'''
	if spl[idx+1] == '/':
		vars_seen.append(spl[idx])
		return False, vars_seen
 	elif (not (spl[idx-1] == '/') and any(char.isalpha() for char in spl[idx]) and spl[idx] not in no_var_list):
		return True, vars_seen
	else:
		return False, vars_seen	


def find_relative_outline_own_chain(cur_path, var_path):
	'''Function that finds the relative path when the reference is part of its own chain'''
	
	output_path_relative = []
	add_number = len(cur_path) - len(var_path)					
	
	if var_path:
		output_path_relative += [var_path[-1]]
	else:										#sometimes we refer to the main node, then just add :start
		output_path_relative += [':start']
	
	out_line = '{' + ' {0} {1}'.format(add_number, " ".join(output_path_relative)) + ' }'
	
	return out_line


def find_relative_outline(cur_path, var_path):
	'''Function that finds the relative path we insert in the AMR'''
	
	output_path_relative = []
	count_steps = 0
	found_line = False
	out_line = ''
	
	for m in range(0, min(len(var_path), len(cur_path))):
		if var_path[m] == cur_path[m]:					#path is the same, we do not have to go so far back
			count_steps += 1
		else:
			found_line = True
			output_path_relative += var_path[m:]
			add_number = len(cur_path) - count_steps
			out_line = '{' + ' {0} {1}'.format(add_number, " ".join(output_path_relative)) + ' }'
			#print out_line
			break											#paths do not match anymore, we can break after adding the rest of the absolute path
	
	return out_line


def find_cur_path_addition(cur_path, spl, idx, all_paths):
	'''Function that finds what we have to add to our current path'''
	
	counter = 1
	found_before = False
	for c in range(15,1,-1):
		to_add = "".join(cur_path) + spl[idx-1] + '|{0}|'.format(c)		#if there are multiple occurences, add the next one (2,3,4,5 etc)
		if to_add in all_paths:
			counter = c
			found_before = True
			break
		prev_add = to_add	
	
	if not found_before:
		counter = 1
	
	cur_path.append(spl[idx-1] + '|{0}|'.format(counter))
	all_paths.append(prev_add)
	
	if len(all_paths) != len(set(all_paths)):
		print 'Something is wrong'
	
	return cur_path, all_paths


def reformat_line(line):
	amr_string = ''
	num_tabs = 0
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
	
	return amr_string


def replace_variables(amrs):
	new_amrs = []
	for a in amrs:
		add_enter = re.sub(r'(:[a-zA-Z0-9-]+)(\|\d\|)',r'\1 \2',a)
		deleted_var_string = re.sub(r'\((.*?/)', '(', add_enter).replace('( ', '(')
		new_amrs.append(deleted_var_string)
	return new_amrs	


def replace_coreference(one_line_amrs, sents):
	'''Function that replaces coreference entities by its relative or absolute path
	   Also normalizes the input, references to variables can not be before instantiation'''
	
	cur_amr = []
	new_amrs = []
	amrs = [x.replace('(',' ( ').replace(')',' ) ').split() for x in one_line_amrs]	# "tokenize" AMRs
	no_var_list = ['interrogative','expressive','imperative']						# we always skip stuff such as :mode interrogative as possible variables
	path_dict = {}
	
	coref_amrs = []
	
	for count, spl in enumerate(amrs):
		if count % 5000 == 0:
			print 'At AMR: {0}'.format(count)
		var_dict = get_var_dict(spl)	#find the path for each variable, save in dict								
		
		cur_path = []
		all_paths = []
		new_spl = []
		vars_seen = []
		level, previous_open, previous_close, added_var, printed = 0, False, False, False, False
		
		for idx in range(1, len(spl)):	#skip first parenthesis to make things easier, add later
			new_spl.append(spl[idx])	#add all parts, if it is a variable and needs changing we do that later
			
			if idx == (len(spl) -1):	#skip last item, never coreference variable
				continue
			
			var_check, vars_seen = variable_match(spl, idx, no_var_list, vars_seen) 		#check if entity looks like a coreference variable
			
			if spl[idx] == '(':
				level += 1
				cur_path, all_paths = find_cur_path_addition(cur_path, spl, idx, all_paths)		#opening parenthesis, means we have to add the previous argument to our path
				previous_close = False
			
			elif spl[idx] == ')':
				level -= 1
				previous_close = True
			
			elif previous_close:				#we previously saw a closing parenthesis, means we have finished the last part of our path	
				cur_path = cur_path[0:level]
				previous_close = False
				
			elif var_check:				#boolean that checked whether it is a variable
				previous_close = False
				
				if not (spl[idx].startswith(':') or spl[idx].startswith('"')):	#not a relation or value, often re-entrancy, check whether it exists
					if spl[idx] in var_dict:									#found variable, check paths
						if spl[idx] not in vars_seen:							#we see a reference, but haven't seen the variable yet
							#print vars_seen
							#print count, spl[idx]
							pass #TODO: implement this later
						
						if spl[idx-1].startswith(':'):							#we skipped this part of the path because it doesn't start with a parenthesis, still add it here
							cur_path, all_paths = find_cur_path_addition(cur_path, spl, idx, all_paths)
						
						if spl[idx] not in new_spl[0:-1]:
							if not printed:
								printed = True
						
						if args.p == 'rel':
							var_path = var_dict[spl[idx]][1].split()				#var_path is the absolute path
							out_line = find_relative_outline(cur_path, var_path)	#out_line for relative path
							
							if not out_line:										#only happens when variable is part of its own chain, then just go back and add last instance of the var_path		
								out_line = find_relative_outline_own_chain(cur_path, var_path)
							
							new_spl[-1] = out_line									#change the previously saved part to the outline here
						else:
							#print new_spl[-1]
							#print " ".join(spl),'\n'
							out_line = '{ ' + var_dict[spl[idx]][1]	+ ' }'
							new_spl[-1] = out_line
							#print out_line
							add_path = var_dict[spl[idx]][1]
							
							if not coref_amrs or coref_amrs[-1] != count:		#check if we already added this AMR
								coref_amrs.append(count)
							
							if add_path not in path_dict:
								path_dict[add_path] = 1
							else:	
								path_dict[add_path] += 1
						#print 'For {0} in AMR {1}'.format(spl[idx], count)
						#print sents[count]
						#print out_line,'\n'				
			else:
				previous_close = False											#we saw a non-interesting entity, just continue	
		

		new_line = '(' + " ".join(new_spl)
		while ' )' in new_line or '( ' in new_line:								#reverse the tokenization process
			new_line = new_line.replace(' )',')').replace('( ','(')
			
		new_amrs.append(new_line)
	
	print 'Length of AMRs with coref: {0}'.format(len(coref_amrs))
	
	assert len(amrs) == len(new_amrs)
	
	total, once = 0, 0
	max_len = 0
	
	for key in path_dict:
		total += 1
		if path_dict[key] == 1:
			once += 1
		
		if len(key.split()) > max_len:
			max_len = len(key.split())
			long_path = key
	
	print 'Longest path: {0}\nOf length: {1}\n'.format(max_len, long_path)			
	print '{0} out of {1} are unique'.format(once, total)		
	return new_amrs	

def create_output(train_f, single_amrs):	
	
	with open(train_f,'w') as f:
		for l in single_amrs:
			f.write(l.strip() + '\n')	
	f.close()				


if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.extension):
				print f
				f_path = os.path.join(root, f)
				amr_file_no_wiki 	= delete_wiki(f_path)
				single_amrs, sents 	= single_line_convert(amr_file_no_wiki)
				repl_amrs  			= replace_coreference(single_amrs, sents)
				final_amrs 			= replace_variables(repl_amrs)
				
				out_f = args.f + f.replace(args.extension,args.output_ext)
				out_f_sents = args.f + f.replace(args.extension, '.sent')
				
				#create_output(out_f, final_amrs)
				#create_output(out_f_sents, sents)
