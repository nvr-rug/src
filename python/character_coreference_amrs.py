#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that converts the AMRs to a single line, taking care of re-entrancies in a nice way by adding special characters'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains the amrs")
parser.add_argument('-extension', required = False, default = '.txt', help="extension of AMR files (default .txt)")
parser.add_argument('-output_ext', required = False, default = '.tf', help="extension of output AMR files (default .tf)")
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
	#print len(single_amrs), len(sents)
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


def variable_match(spl, idx, no_var_list):
	'''Function that matches entities that are variables occurring for the second time'''
	if idx >= len(spl) or idx == 0:
		return False
	
 	if (not spl[idx-1] == '/' and any(char.isalpha() for char in spl[idx]) and spl[idx] not in no_var_list and not spl[idx].startswith(':') and len([x for x in spl[idx] if x.isalpha() or x.isdigit()]) == len(spl[idx]) and (len(spl[idx]) == 1 or (len(spl[idx]) > 1 and spl[idx][-1].isdigit()))):
		#print spl[idx]
		return True
	else:
		return False
		

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
	'''Function that replaces coreference entities by its relative or absolute path'''
	
	new_amrs = []
	amrs = [x.replace('(',' ( ').replace(')',' ) ').split() for x in one_line_amrs]	# "tokenize" AMRs
	no_var_list = ['interrogative','expressive','imperative']						# we always skip stuff such as :mode interrogative as possible variables
	
	for count, spl in enumerate(amrs):						
		#print '\ncount {0}\n'.format(count+1)
		all_vars = []
		
		for idx in range(0, len(spl)):
			if variable_match(spl, idx, no_var_list): 		#check if entity looks like a coreference variable				
				all_vars.append(spl[idx])
		
		vars_seen = []
		new_spl = []	
		
		for idx in range(0, len(spl)):
			if variable_match(spl, idx, no_var_list): 		#check if entity looks like a coreference variable				
				if all_vars.count(spl[idx]) > 1:			#if entity occurs at least twice, make mention of it
					if spl[idx] in vars_seen:
						print 'Ref found'
						new_spl.append('*{0}*'.format(vars_seen.index(spl[idx])))
					else:
						new_spl.append('*{0}*'.format(len(vars_seen)))
						vars_seen.append(spl[idx])
					 
					#print new_spl[-1]
			elif spl[idx] != '/':		#part of variable, skip
				new_spl.append(spl[idx])
							
					
		new_line = " ".join(new_spl)
		while ' )' in new_line or '( ' in new_line:								#reverse the tokenization process
			new_line = new_line.replace(' )',')').replace('( ','(')
		
		#print new_line	
		new_amrs.append(new_line)
	
	assert len(amrs) == len(new_amrs)

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
				f_path = os.path.join(root, f)
				amr_file_no_wiki 	= delete_wiki(f_path)
				single_amrs, sents 	= single_line_convert(amr_file_no_wiki)
				repl_amrs  			= replace_coreference(single_amrs, sents)
				
				out_f = args.f + f.replace(args.extension,args.output_ext)
				out_f_sents = args.f + f.replace(args.extension, '.sent')
				
				#create_output(out_f, repl_amrs)
				#create_output(out_f_sents, sents)
