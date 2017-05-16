#!/usr/bin/env python
# -*- coding: utf8 -*-

import re,sys, argparse, os, random, collections, subprocess, json
reload(sys)
import validator_seq2seq

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="File with AMRs (one line)")
parser.add_argument("-out_ext", default = '.check', type=str, help="Extension of output files")
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


def do_string_adjustments(permutations_new, keep_string2,  indx):
	add_string = keep_string2 + ' ' + " ".join(permutations_new) + ' '
	
	while add_string.count(')') < add_string.count('('): 			## check if we need to add a parenthesis
		add_string += ')' 											## avoid extra unnecessary space
	
	return add_string


def get_add_string(search_part):
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
		if ')' not in p or '(' not in p:				#length always 1
			if p.count(':') > 2:
				p_split = p.split(':')[1:]
				new_perms = [':' + x.strip() for x in p_split]
				return add_string, new_perms			

	return add_string, permutations			


def nice_print_amr(line):
	prev_ch = ''
	fixed_amrs = []
	num_tabs = 0
	amr_string = ''
	
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
			
	print (amr_string)


def get_best_perm(permutations, final_string, all_perms, prop_dict):
	
	'''This must also be possible recursive'''
	
	
	for indx2, p2 in enumerate(permutations):
		permutations_2, keep_string2, all_perms = get_permutations(p2,2, all_perms, prop_dict)
		
		for indx3, p3 in enumerate(permutations_2):
			permutations_3, keep_string3, all_perms = get_permutations(p3,3, all_perms, prop_dict)
			
			for indx4, p4 in enumerate(permutations_3):
				permutations_4, keep_string4, all_perms = get_permutations(p4,4, all_perms, prop_dict)
			
				for indx5, p5 in enumerate(permutations_4):
					permutations_5, keep_string5, all_perms = get_permutations(p5,5, all_perms, prop_dict)
					
					for indx6, p6 in enumerate(permutations_5):
						permutations_6, keep_string6, all_perms = get_permutations(p6, 6 , all_perms, prop_dict)
						
						for indx7, p7 in enumerate(permutations_6):
							permutations_7, keep_string7, all_perms = get_permutations(p7, 7, all_perms, prop_dict)
							
							for indx8, p8 in enumerate(permutations_7):
								permutations_8, keep_string8, all_perms = get_permutations(p8,8, all_perms, prop_dict)
								
								for indx9, p9 in enumerate(permutations_8):
									permutations_9, keep_string9, all_perms = get_permutations(p9,9, all_perms, prop_dict)
									
									for indx10, p10 in enumerate(permutations_9):
										permutations_10, keep_string10, all_perms = get_permutations(p10,10, all_perms, prop_dict)
										
										for indx11, p11 in enumerate(permutations_10):
											permutations_11, keep_string11, all_perms = get_permutations(p11,11, all_perms, prop_dict)
											
											for indx12, p12 in enumerate(permutations_11):
												permutations_12, keep_string12, all_perms = get_permutations(p12,12, all_perms, prop_dict)
												add_string = do_string_adjustments(permutations_12, keep_string12, indx12)
												keep_string11 += add_string.replace('  ',' ')
										
											keep_string10 += fix_paren(keep_string11)
										
										keep_string9 += fix_paren(keep_string10)
									
									keep_string8 += fix_paren(keep_string9)
									
								keep_string7 += fix_paren(keep_string8)
							
							keep_string6 += fix_paren(keep_string7)				
	
						keep_string5 += fix_paren(keep_string6)
							
					keep_string4 += fix_paren(keep_string5)
				
				keep_string3 += fix_paren(keep_string4)
				
			keep_string2 += fix_paren(keep_string3)
				
		final_string += fix_paren(keep_string2)
			
	final_string = fix_paren(final_string)
	
	return final_string	


def get_keep_string(new_parts, level):
	'''Obtain string we keep, it differs for level 1'''
	
	if level > 1:
		keep_string = ':' + ":".join(new_parts[:1])
	else:
		keep_string = ":".join(new_parts[:1])
	search_part = ':' + ":".join(new_parts[1:])
	
	return keep_string, search_part


def fix_paren(string):
	while string.count('(') > string.count(')'):
		string += ')'
	
	return string
	

def combine_permutations(permutations, cut_off):
	'''Combine permutations if they exceed the cut-off specified'''
	
	if len(permutations) > cut_off:
		shuffle(permutations)
		permutations = permutations[0:args.cut_off - 1] + [" ".join(permutations[args.cut_off - 1:])]	# just add extra permutations to the last permutation
	
	return permutations


def create_final_line(final_string):
	'''Do final adjustments for line, including some lame bugfixes for now'''
	
	add_to = final_string.replace('  ',' ') .strip()
	while ' )' in add_to:
		add_to = add_to.replace(' )',')')
	
	add_to = fix_paren(add_to)	
	add_to = add_to.replace('):',') :')
	add_to = add_to.replace(' :)',')')
	add_to = add_to.replace(': :',':')
		
	return add_to


def get_new_sense(prop_dict, keep_string, verb):
	'''Verb has impossible sense, if possible, change it'''
	
	clean_verb = re.sub(r'-\d\d','',verb)
	poss_senses = []
	for key in prop_dict:
		clean_key = re.sub(r'-\d\d','', key)
		if clean_key == clean_verb:
			sense = re.findall(r'-[\d]+', key)
			poss_senses.append(sense[0].replace('-',''))
		
	if poss_senses:		#verb has impossible sense, but there is a possible sense available in propbank
		new_sense = min([int(x) for x in poss_senses])
		
		if new_sense < 10:			#add 0 for verb-01 instead of verb-1
			str_sense = '0' + str(new_sense)
		else:
			str_sense = str(new_sense)	
		
		new_verb = re.sub(r'-[\d]+','-' + str_sense, verb)
		keep_string = keep_string.replace(verb, new_verb)
		#print 'Changed sense of {0} to {1}'.format(verb, new_verb)
		return keep_string, new_verb, True
	else:
		return keep_string, verb, False		


def find_fitting_sense(verb, prop_dict, all_args):
	other_senses = []
	clean_verb = re.sub(r'-\d\d','',verb)
	for key in prop_dict:
		clean_key = re.sub(r'-\d\d','', key)
		if clean_key == clean_verb and key != verb:
			other_senses.append(key)
	
	for v in other_senses:
		possible_args = prop_dict[v]					#arguments possible for this other sense
		if set(all_args).issubset(set(possible_args)):	#check if all arguments are possible
			return v									#return first fitting new sense
	
	return ''	#return empty
			
	#possible check for frequency here, don't change sense if it's the most frequent sense -> change argument instead


def sense_arg_mismatch(verb, prop_dict, all_args):
	for a in all_args:
		if a not in prop_dict[verb]:	#there is a mismatch if an argument of the verb is not in the prop-dict of the verb
			#print 'Mismatch for {0}, {1}'.format(verb, a)
			return True
	
	#print 'No mismatch for {0}, {1}'.format(verb, all_args)
	return False		


def get_permutations(part, level, all_perms, prop_dict):	
	
	part = part[1:] 																			# make life easier by skipping first '(' or ':'  										# get all words in sentence in lower case
	
	if ':' not in part or (part.count(':') == 1 and ('http:' in part or 'https:' in part)):		# if there is nothing to change then we return
		if level == 1:
			return [part], '', all_perms
		else:	
			return [':' + part], ''	, all_perms

	new_parts 				 = filter_colons(part)												#remove non-arguments that have a colon such as timestamps and websites
	keep_string, search_part = get_keep_string(new_parts, level)
	add_string, permutations = get_add_string(search_part)		
	permutations_set = []
	
	verbs = re.findall(r'[^ ]+-\d\d',keep_string)		#filter for possible verbs - e.g. not all verbs can have ARG2
	all_args = [p.split()[0] for p in permutations if 'ARG' in p.split()[0]]

	if len(verbs) > 0:
		verb = re.sub(r'[\(\)\"\']','',verbs[0])
		valid_verb = True
		if verb not in prop_dict:
			keep_string, verb, valid_verb = get_new_sense(prop_dict, keep_string, verb)	#possibly change the sense
		
		if valid_verb:					#check if verb is still valid and in prop dict
			if sense_arg_mismatch(verb, prop_dict, all_args):	#check for mismatch in sense and arguments
				fitting_sense = find_fitting_sense(verb, prop_dict, all_args)	#is there a fitting sense available?
				if fitting_sense:
					keep_string = keep_string.replace(verb, fitting_sense)
				else:
					for idx in range(0, len(permutations)):
						spl_p = permutations[idx].split()
						arg = spl_p[0]
						if 'ARG' in arg and arg not in prop_dict[verb]:
							repl = False
							for poss_arg in prop_dict[verb]:
								if poss_arg not in all_args and '-of' not in poss_arg:
									spl_p[0] = spl_p[0].replace(arg, poss_arg)
									permutations[idx] = " ".join(spl_p)
									repl = True
									break	
							
							if not repl:		#we did not find a suitable replacement	
								#if permutations[idx].count(':') < 2:	#if single permutation, just remove the whole thing
								#	permutations[idx] = ''
								#else:
								first_arg = prop_dict[verb][0]						#otherwise, just chagge into the first possible argument
								spl_p[0] = spl_p[0].replace(arg, first_arg)
								permutations[idx] = " ".join(spl_p)
	
	permutations = [p for p in permutations if p]
	all_perms += permutations
	
	return permutations, keep_string, all_perms


def has_numbers(inputString):
	return any(char.isdigit() for char in inputString)


def get_prop_bank_args():
	prop_dict = {}
	
	verbs = [x.strip() for x in open('/home/p266548/Documents/amr_Rik/data_2017_fixed_unicode/data/frames/propbank-frame-arg-descr.txt','r')]
	for idx, v in enumerate(verbs):
		verb = v.split('  ')[0]
		args = [':' + x.split()[0].replace(':','') for x in v.split('  ')[1:]]	#get all possible arguments
		fil_args = [x for x in args if x.startswith(':ARG') and has_numbers(x)]	#filter nonsense arguments
		new_items = [x for x in fil_args]
		for item in fil_args:
			of_item = item + '-of'
			if of_item not in fil_args:
				new_items.append(of_item)
		prop_dict[verb] = new_items
	return prop_dict


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()


def check_errors(amrs):
	new_amrs = []
	
	for line in amrs:
		new_line = re.sub(r'(:[a-zA-Z]+)([0-9]+)\.',r'\1 \2', line)	#fix weird errors such as :quant7. :arg12. etc. Fix this sometime to see how they even got in
		new_amrs.append(new_line)
	
	return new_amrs	


if __name__ == '__main__':
	
	filtered_amrs = []
	changed, invalid = 0, 0
	prop_dict = get_prop_bank_args()
	
	
	for idx, line in enumerate(open(args.f,'r')):
		clean_line = re.sub(r'\([A-Za-z0-9-_~]+ / ',r'(', line).strip()	#delete variables
		if clean_line.count(':') > 1:		#only try to do something if we can actually permutate					
			permutations, keep_string1, all_perms = get_permutations(clean_line,1,[], prop_dict)
			keep_str = '(' + keep_string1
			final_string = get_best_perm(permutations,  keep_str, all_perms, prop_dict)
			add_to = create_final_line(final_string)
			filtered_amrs.append(add_to)
			if add_to != clean_line:
				changed += 1

		else:
			filtered_amrs.append(clean_line.strip())
	
	print '\t\tChanged {0} AMRs by changing invalid arguments/senses'.format(changed)
	
	filtered_amrs = check_errors(filtered_amrs)
	
	out_file_fil = args.f + '.check_temp'
	write_to_file(filtered_amrs, out_file_fil)
	
	restore_new = out_file_fil.replace('.check_temp',args.out_ext)
	restore_call = 'python /home/p266548/Documents/amr_Rik/Seq2seq/src/python/restoreAMR/restore_amr.py {0} > {1}'.format(out_file_fil, restore_new)
	os.system(restore_call)

	os.system("rm {0}".format(out_file_fil))	#remove temp file again
	
	fix_amrs = [x.strip() for x in open(restore_new, 'r')]
	fixed_amrs = check_errors(fix_amrs)
	write_to_file(fixed_amrs, restore_new)
