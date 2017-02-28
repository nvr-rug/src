#!/usr/bin/env python
# -*- coding: utf8 -*-

import re,sys, argparse, os, random, collections, subprocess, json
reload(sys)
import validator_seq2seq

parser = argparse.ArgumentParser()
parser.add_argument("-f", required = True, type=str, help="File with AMRs (one line)")
#parser.add_argument("-b", required = True, type=str, help="Bio-test AMRs (one line)")
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


def get_best_perm(permutations, final_string, all_perms):
	
	'''This must also be possible recursive'''
	
	
	for indx2, p2 in enumerate(permutations):
		permutations_2, keep_string2, all_perms = get_permutations(p2,2, all_perms)
		
		for indx3, p3 in enumerate(permutations_2):
			permutations_3, keep_string3, all_perms = get_permutations(p3,3, all_perms)
			
			for indx4, p4 in enumerate(permutations_3):
				permutations_4, keep_string4, all_perms = get_permutations(p4,4, all_perms)
			
				for indx5, p5 in enumerate(permutations_4):
					permutations_5, keep_string5, all_perms = get_permutations(p5,5, all_perms)
					
					for indx6, p6 in enumerate(permutations_5):
						permutations_6, keep_string6, all_perms = get_permutations(p6, 6 , all_perms)
						
						for indx7, p7 in enumerate(permutations_6):
							permutations_7, keep_string7, all_perms = get_permutations(p7, 7, all_perms)
							
							for indx8, p8 in enumerate(permutations_7):
								permutations_8, keep_string8, all_perms = get_permutations(p8,8, all_perms)
								
								for indx9, p9 in enumerate(permutations_8):
									permutations_9, keep_string9, all_perms = get_permutations(p9,9, all_perms)
									
									for indx10, p10 in enumerate(permutations_9):
										permutations_10, keep_string10, all_perms = get_permutations(p10,10, all_perms)
										
										for indx11, p11 in enumerate(permutations_10):
											permutations_11, keep_string11, all_perms = get_permutations(p11,11, all_perms)
											
											for indx12, p12 in enumerate(permutations_11):
												permutations_12, keep_string12, all_perms = get_permutations(p12,12, all_perms)
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


def get_permutations(part, level, all_perms):	
	
	part = part[1:] 																			# make life easier by skipping first '(' or ':'  										# get all words in sentence in lower case
	
	if ':' not in part or (part.count(':') == 1 and ('http:' in part or 'https:' in part)):		# if there is nothing to change then we return
		if level == 1:
			return [part], '', all_perms
		else:	
			return [':' + part], ''	, all_perms

	new_parts 				 = filter_colons(part)												#remove non-arguments that have a colon such as timestamps and websites
	keep_string, search_part = get_keep_string(new_parts, level)
	add_string, permutations = get_add_string(search_part)
	
	#if len(permutations) != len(set(permutations)):
		#permutations_set = []
		#for p in permutations:
		#	if p not in permutations_set:
		#		permutations_set.append(p)
		#permutations_set = list(set(permutations))
		#print 'Change', len(permutations) - len(set(permutations))
			
	permutations_set = []
	
	
	for p in permutations:
		if p in permutations_set:
			continue
		elif p not in all_perms:
			permutations_set.append(p)
		elif all_perms.count(p) < 2:
			permutations_set.append(p)
	all_perms += permutations
	
	#for x in range(len(permutations) - len(permutations_set)):
	#	print 'change'
	
	return permutations_set, keep_string, all_perms


def analyse_each(new_amr, old_amr, bio_amr):
	with open('new_amr.txt','w') as out_f:
		out_f.write(new_amr.strip() + '\n')
	out_f.close()
	
	with open('old_amr.txt','w') as out_f:
		out_f.write(old_amr.strip() + '\n')
	out_f.close()
	
	with open('bio_amr.txt','w') as out_f:
		out_f.write(bio_amr.strip() + '\n')
	out_f.close()	
	
	restore_call = 'python restoreAMR/restore_amr.py new_amr.txt > new_amr.txt.restore'
	os.system(restore_call)
	
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r 4 --both_one_line -f old_amr.txt bio_amr.txt'
	output = subprocess.check_output(os_call, shell=True)
	f_score_old = float(output.split()[-1])
	
	os_call = 'python ~/Documents/amr_Rik/Seq2seq/src/python/smatch_2.0.2/smatch.py -r 4 --both_one_line -f new_amr.txt.restore bio_amr.txt'
	output = subprocess.check_output(os_call, shell=True)
	f_score_new = float(output.split()[-1])
	
	if f_score_old > f_score_new:
		print 'worse'
		#print f_score_old, f_score_new
		#print old_amr
		#print new_amr
		#print bio_amr,'\n'
	else:
		print 'better'	
	

if __name__ == '__main__':
	
	filtered_amrs = []
	changed, invalid = 0, 0
	#bio_amrs = [x.strip() for x in open(args.b, 'r')]
	
	for idx, line in enumerate(open(args.f,'r')):
		clean_line = re.sub(r'\([A-Za-z0-9-_~]+ / ',r'(', line).strip()	#delete variables
		if clean_line.count(':') > 1:		#only try to do something if we can actually permutate					
			permutations, keep_string1, all_perms = get_permutations(clean_line,1,[])
			keep_str = '(' + keep_string1
			final_string = get_best_perm(permutations,  keep_str, all_perms)
			add_to = create_final_line(final_string)
			filtered_amrs.append(add_to)
			if add_to != clean_line:
				#analyse_each(add_to, line, bio_amrs[idx])
				changed += 1
				#nice_print_amr(add_to)
				#nice_print_amr(clean_line)
				#print '\n'

		else:
			filtered_amrs.append(clean_line.strip())
	
	print 'Changed {0} AMRs'.format(changed)
	
	out_file_fil = args.f + '.pruned_temp'
	
	with open(out_file_fil,'w') as out_f:
		for a in filtered_amrs:
			out_f.write(a.strip() + '\n')
	out_f.close()
	
	restore_new = out_file_fil.replace('.restore.pruned_temp','.restore.pruned')
	restore_call = 'python /home/p266548/Documents/amr_Rik/Seq2seq/src/python/restoreAMR/restore_amr.py {0} > {1}'.format(out_file_fil, restore_new)
	os.system(restore_call)

	os.system("rm {0}".format(out_file_fil))	#remove temp file again
	
