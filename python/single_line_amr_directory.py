#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os

'''Script that converts the AMRs to a single line
   Presupposes that files have a certain extension (default .txt)'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains the amrs")
parser.add_argument('-extension', required = False, default = '.txt', help="extension of AMR files (default .txt)")
parser.add_argument('-output_ext', required = False, default = '.tf', help="extension of output AMR files (default .tf)")
parser.add_argument('-sent_ext', required = False, default = '.sent', help="extension of sentences (default .sent)")
args = parser.parse_args()

def single_line_convert(f):
	single_amrs = []
	prev_amr = False
	for line in f:
		if line[0] != '#':					# skip non-amr lines
			if prev_amr:
				amr.append(line.strip())
			else:
				amr = [line]
			prev_amr = True
		else:									# start a new AMR to convert
			if prev_amr:
				single_line_amr = " ".join(amr)
				single_amrs.append(single_line_amr)
			prev_amr = False
			single_amrs.append(line)		# add the line with hashtag info as well

	if amr != []:
		single_line_amr = " ".join(amr)
		single_amrs.append(single_line_amr)				# last one is not automatically added due to missing '#'

	return single_amrs


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
	

def delete_amr_variables(amrs):
	'''Function that deletes variables from AMRs'''
	var_dict = dict()
	del_amr = []
	num_amrs = 0
	sents = []
	
	for line in amrs:	
		if not line.strip():
			continue
		elif line.startswith('# ::snt'):
			sents.append(line.replace('# ::snt','').strip())
			num_amrs += 1
			printed = False
		elif line[0] != '#':
			if '/' in line:		# variable here
				deleted_var_string, var_dict = process_var_line(line, var_dict)						# process line and save variables
				del_amr.append(deleted_var_string)													# save string with variables deleted

			else:				# (probable) reference to variable here!
				split_line = line.split()
				ref_var = split_line[1].replace(')', '')											# get var name
				if ref_var in var_dict:
					if not printed:
						printed = True

					ref_value = var_dict[ref_var]													# value to replace the variable name with
					split_line[1] = split_line[1].replace(ref_var, '(' + ref_value.strip() + ')')   # do the replacing and add brackets for alignment
					n_line = (len(line) - len(line.lstrip())) * ' ' + " ".join(split_line)
					del_amr.append(n_line)
				else:
					del_amr.append(line)	# no reference found, add line without editing (usually there are numbers in this line)
		else:
			del_amr.append(line)

	return del_amr, sents


def write_to_file(l, f):
	with open(f,'w') as out_f:
		for line in l:
			out_f.write(line.strip() + '\n')
	out_f.close()


if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.extension):
				f_path = os.path.join(root, f)
				amr_file_no_wiki = delete_wiki(f_path)
				del_amrs, sents = delete_amr_variables(amr_file_no_wiki)

				single_amrs = single_line_convert(del_amrs)
				single_amrs_train = [x for x in single_amrs if len(x) > 0 and x[0] != '#' ]
				
				assert len(single_amrs_train) == len(sents)
				
				out_tf = f_path.replace(args.extension,args.output_ext)
				out_sent = f_path.replace(args.extension, args.sent_ext)
				
				write_to_file(single_amrs_train, out_tf)
				write_to_file(sents, out_sent)
