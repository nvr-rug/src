import sys
import re
import argparse
import os
import validator_seq2seq

'''Script that adds coreferents back in produced AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="File that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.restore.wiki',  required=False, type=str, help="Input extension of AMRs (default .restore.wiki)")
parser.add_argument("-output_ext", default = '.coref', required=False, type=str, help="Output extension of AMRs (default .coref)")
args = parser.parse_args()


def process_var_line(line, f):
	'''Function that processes line with a variable in it. Returns the string without 
	   variables and the dictionary with var-name + var - value'''

	var_list = []
	curr_var_name, curr_var_value = False, False
	var_value , var_name = '', ''
	skip_first = True
	
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
				if not var_list and skip_first:
					skip_first = False				#skip first entry, but only do it once. We never want to refer to the full AMR.
				else:	
					add_var_value = var_value.strip().replace(')','')
					var_list.append([var_name.strip(), add_var_value])
			var_name = ''
			continue	
		
		if curr_var_name:		# add to variable name
			var_name += ch
		elif curr_var_value:		# add to variable value
			var_value += ch
	
	var_list.append([var_name.strip(), var_value.strip().replace(')','')])	#add last one
	
	for item in var_list:
		try:
			if not item[1].split()[-1].isdigit() and len(item[1].split()) > 1:			#keep in :quant 5 as last one, but not ARG1: or :mod
				item[1] = " ".join(item[1].split()[0:-1])
		except:
			print 'Small error, just ignore'		
						
	return var_list

def write_to_file(l, f):
	with open(f,'w') as out_f:
		for line in l:
			out_f.write(line.strip() + '\n')
	out_f.close()

def process_file(f):
	
	old_lines = [x for x in open(f,'r')]
	valid, invalid = 0,0
	replace_possible_count = 0
	no_replace, yes_replace = 0,0
	coref_amrs = []
	
	for idx, line in enumerate(old_lines):
		replace_possible = False
		actual_replace = False
		var_list = process_var_line(line, f)
		new_line = line
		for idx in range(len(var_list)-1):
			for y in range(idx+1, len(var_list)):
				if var_list[idx][1] == var_list[y][1]:
					replace_possible = True
					replace_item = var_list[y][0] + ' / ' + var_list[y][1]
					if replace_item in line:
						new_line_replaced = new_line.replace(replace_item, var_list[idx][0])
						new_line_replaced = new_line_replaced.replace('(' + var_list[idx][0] + ')', var_list[idx][0])
						if validator_seq2seq.valid_amr(new_line_replaced):
							yes_replace += 1
							new_line = new_line_replaced
							actual_replace = True
						else:
							no_replace += 1		
		if replace_possible:
			replace_possible_count += 1
			
		if actual_replace:
			if not validator_seq2seq.valid_amr(new_line):
				invalid += 1
			else:
				valid += 1
		
		coref_amrs.append(new_line)					
	
	#print '\n{0} has {1} possible replaceable AMRs out of {2} lines'.format(f.split('/')[-1], replace_possible_count, len(old_lines))
	#print '{0}/{1} were valid for the {2} possible replaces'.format(valid, valid + invalid, replace_possible_count)			
	#print '{0} out of {1} times we did actually replace\n'.format(yes_replace, no_replace + yes_replace)				
	
	assert(len(coref_amrs) == len(old_lines))
	
	return coref_amrs
	
if __name__ == '__main__':
	coref_amrs = process_file(args.f)
	coref_name = args.f + args.output_ext
	write_to_file(coref_amrs, coref_name)
