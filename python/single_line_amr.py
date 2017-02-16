#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import re
import argparse
import os
import shlex
import signal
import subprocess

'''Script that converts the AMRs to a single line, optional to delete variables/wiki information'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="file that contains the amrs")
parser.add_argument('-d', action='store_true', default=False, help="delete variables yes/no")
#parser.add_argument('-o', required = True,help="output-file with '#' info")
parser.add_argument('-tf', required = True, help="output-file without '#' info (trainfile)")
args = parser.parse_args()

delete_variables = args.d

def valid_amr(curr_out):
	validator_call = shlex.split('python ./validator/validator.py --infile {0}'.format(curr_out))
	try:
		output = subprocess.check_output(validator_call, stderr=subprocess.STDOUT)
		if 'Error' in output or 'MAJOR WARNING' in output:
			return False
	except subprocess.CalledProcessError:
		return False

	return True

def single_line_convert(f, print_f):
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


def delete_amr_variables(amrs, print_f):
	var_dict = dict()
	count = 0
	del_amr = []
	prev_amr = False
	for line in amrs:
		count += 1
		num_var = 0
		prev_amr = True
		
		if not line.strip():
			continue
		if line[0] != '#':
			if '/' in line:		# variable here
				for idx, ch in enumerate(line):
					if ch == '(':															# variables are always preceeded by a '('
						var = (line[idx + 1] + line[idx + 2]).strip()							# obtain variable name
						num_var += 1
						part = "(".join(line.split('(')[num_var:]).replace(')', '').strip() 	# obtain variable value
						part = "/".join(part.split('/')[1:])
						deleted_var = re.sub(r'\((.*?) \/', '(', part).replace('( ', '(')			# delete the variables
						if '(' in deleted_var:
							deleted_var += ')'
						var_dict[var] = deleted_var													# add to dict

				deleted_var = re.sub(r'\((.*?/)', '(', line).replace('( ', '(')
				del_amr.append(deleted_var)														# save string with variables deleted

			else:				# (probable) reference to variable here!
				split_line = line.split()
				ref_var = split_line[1].replace(')', '')						# get var name
				if ref_var in var_dict:
					ref_value = var_dict[ref_var]								# value to replace the variable name with
					split_line[1] = split_line[1].replace(ref_var, '(' + ref_value.strip() + ')')   # do the replacing and add brackets for alignment
					n_line = (len(line) - len(line.lstrip())) * ' ' + " ".join(split_line)
					del_amr.append(n_line)
				else:
					del_amr.append(line)	# no reference found, add line without editing (usually there are numbers in this line)
		else:
			del_amr.append(line)

	return del_amr

	
def create_output(train_f, single_amrs):	
	single_amr_train = [x for x in single_amrs if len(x) > 0 and x[0] != '#' ]
	
	with open(train_f,'w') as f:
		for l in single_amr_train:
			f.write(l + '\n')	
		f.close()				

if __name__ == "__main__":
	if delete_variables:
		amr_file_no_wiki = delete_wiki(args.f)
		del_amrs = delete_amr_variables(amr_file_no_wiki, False)
	else:
		del_amrs = [x for x in open(args.f, 'r')]

	single_amrs = single_line_convert(del_amrs, True)
	create_output(args.tf, single_amrs)

