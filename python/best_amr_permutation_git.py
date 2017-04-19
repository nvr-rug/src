import sys,re,os
import argparse
import itertools
import validator_seq2seq
import random
from random import shuffle
import subprocess
import time
import json

'''Script that augments the data to get the best AMR permutation based on word order'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="folder that contains to be processed files")
parser.add_argument("-amr_ext", default = '.txt', type=str, help="AMR extension (default .txt) - should have alignments")
parser.add_argument("-temp_old", default = 'temp_old.txt', type=str, help="Extension of old temp")
parser.add_argument("-temp_new", default = 'temp_new.txt', type=str, help="Extension of new temp")
parser.add_argument("-cut_off", default = 15, type=int, help="When to cut-off number of permutations")
parser.add_argument("-double", default = '', type=str, help="Add best permutation AMR AND normal AMR?")
parser.add_argument("-cleanup", default = '', type=str, help="Delete all non-final files (recommended)")
args = parser.parse_args() 


def get_filenames(f, wf,  new, old, restore, old_sent, new_sent):
	file_new = wf + f + new
	file_old = wf + f + old
	restore_new = file_new +  restore
	restore_old = file_old +  restore
	sent_old = wf + f + old_sent
	sent_new = wf + f + new_sent
	double_sent = wf + f.replace('.txt','.sent')
	double_amr = wf + f.replace('.txt','.tf')
	return file_new, file_old, restore_new, restore_old, sent_old, sent_new, double_sent, double_amr


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
	
	for line in amrs:	
		if not line.strip():
			del_amr.append(' ')
			continue
		elif line[0] != '#':
			if '/' in line:		# variable here
				deleted_var_string, var_dict = process_var_line(line, var_dict)						# process line and save variables
				del_amr.append(deleted_var_string)													# save string with variables deleted

			else:				# (probable) reference to variable here!
				split_line = line.split()
				ref_var = split_line[1].replace(')', '')											# get var name
				ref_var_no_sense = split_line[1].replace(')', '').split('~')[0]
				if ref_var_no_sense in var_dict:
					ref_value = var_dict[ref_var_no_sense]											# value to replace the variable name with
					split_line[1] = split_line[1].replace(ref_var, '(' + ref_value.strip() + ')')   # do the replacing and add brackets for alignment
					n_line = (len(line) - len(line.lstrip())) * ' ' + " ".join(split_line)
					del_amr.append(n_line)
				else:
					del_amr.append(line)	# no reference found, add line without editing (usually there are numbers in this line)
		else:
			del_amr.append(line)

	return del_amr


def get_tokenized_sentences(f):
	sents = [l.replace('# ::tok','').strip() for l in open(f,'r') if l.startswith('# ::tok')]
	return sents


def delete_wiki(f):
	'''Removes wiki links from AMR'''
	
	no_wiki = []
	for line in open(f, 'r'):
		n_line = re.sub(r':wiki "(.*?)"', '', line, 1)
		n_line = re.sub(':wiki -', '', n_line)
		no_wiki.append((len(n_line) - len(n_line.lstrip())) * ' ' + ' '.join(n_line.split()))  # convert double whitespace but keep leading whitespace
	return no_wiki


def single_line_amrs(amrs):
	'''Convert AMR structure to single-line AMR'''
	
	all_amrs = []
	curr_amr = []
	
	for idx, line in enumerate(amrs):
		if line[0] == '#':
			continue
		elif line.strip() == '' and curr_amr:				# when we encounter newline we know that previous AMR is done
			single_line = " ".join(curr_amr)
			all_amrs.append(single_line.strip())
			curr_amr = []
		else:
			curr_amr.append(line.strip())
	
	if curr_amr:
		single_line = " ".join(curr_amr)
		all_amrs.append(single_line.strip())
	
		
	return all_amrs


def write_to_file(new_amrs, file_new):
	with open(file_new,'w') as out_f:
		for line in new_amrs:
			out_f.write(line.strip() + '\n')
	out_f.close()


def restore_amrs(file_new, restore_new):
	restore_call = 'python restoreAMR/restore_amr.py {0} > {1}'.format(file_new, restore_new)
	os.system(restore_call)			


def remove_sense(string):
	 string = re.sub('~e\.[\d,]+','', string)
	 return string


def get_word_and_sense(line):
	'''Character based extraction because I couldn't figure it out using regex'''
	
	quotes = 0
	adding = False
	comb = []
	word = ''
	if '"' in line:
		for idx, ch in  enumerate(line):
			if ch == '"':
				quotes += 1
				if quotes % 2 != 0:
					adding = True
				else:					# finished quotations
					comb.append([word])
					word = ''
					adding = False
			elif ch == '~':
				if adding:
					word += ch
				elif ':op' in "".join(line[idx-4:idx-1]):		#bugfix for strange constructions, e.g. name :op1~e.4 "Algeria"~e.2 
					continue	
				else:	
					if idx+4 < len(line):
						sense_line = line[idx+1] + line[idx+2] + line[idx+3] + line[idx+4]
					else:
						sense_line = line[idx+1] + line[idx+2] + line[idx+3]	
					sense = int("".join([s for s in sense_line if s.isdigit()]))
					try:
						comb[-1].append(sense)
					except:
						pass		
			else:
				if adding:
					word += ch
				else:
					continue
	elif ':op' not in line:
		return [['','']]
	else:
		tmp = line.split()[2]		
		sense, word = get_sense(tmp)
		
		
		comb = [[word,sense]]		 
	return comb				

def get_sense(word):
	'''Function that gets the sense of a certain word in aligned AMR'''
	
	if '~' in word:
		sense = word.split('~')[-1].split('.')[-1] 		# extract 16 in e.g. house~e.16
		
		if ',' in sense:								# some amr-words refer to multiple tokens. If that's the case, we take the average for calculating distance
														# although this means that the actual sense does not refer to the tokens anymore (# e.g. the sense of house~e.4,12 becomes 8)			
			sense = round((float(sum([int(i) for i in sense.split(',')]))) / (float(len(sense.split(',')))),0)
		else:
			sense = int(sense)	
														
		word = word.split('~')[0]							# remove sense information to process rest of the word
	else:
		sense = ''	
	
	return sense, word
	
				
def find_words(line):
	'''Finds all words in the AMR structure'''
	
	comb = []
	spl_line = line.split('(')
	if '(' not in line:
		if line.count('~') > 0 and len(line.split()) > 1:
			sense, word = get_sense(line.split()[1])
			return [[word, sense]]
		else:
			return [['none-found',0]]	
	else:	
		for idx in range(1, len(spl_line)):
			if spl_line[idx]:
				word = spl_line[idx].strip().split()[0].replace(')','')
				if word == 'name':											#name gets special treatment by AMRs
					cut_word = spl_line[idx].split(')')[0]
					comb += get_word_and_sense(cut_word)	
				else:	
					sense, word = get_sense(word)
					num_digits = sum(c.isdigit() for c in word)
					
					if word.count('-') == 1 and num_digits < 3 and num_digits > 0:				# tricky: we want to change break-01 to break, but do not want to screw up dates (08-09-2016 or 28-10)
						word = word.split('-')[0]
					comb.append([word,sense])
	
	for idx in range(len(comb)):
		if len(comb[idx]) < 2:
			comb[idx].append('')		#add empty sense
	
	return comb	


def matching_words(permutations):
	'''Finds all words in different order for all the permutations'''
	
	all_found = []
	
	for per in permutations:
		found_words = find_words(per)
		if found_words:
			all_found.append(find_words(per))
	
	return all_found		


def calc_distance(l):
	'''Calculates distance between list items in 2 two lists'''
	
	#l needs to start from zero, get lowest number and substract it from all numbers
	
	min_l = min([x[1] for x in l if x != ''])
	l = [[x[0], (x[1] - min_l)] for x in l if x[1]!= '']

	distance = 0
	
	for idx, item in enumerate(l):
		if len(item) > 1 and item[1] != '':					#check if we found a sense
			diff = abs(item[1] - idx)		#check how far away we are in our token list
			distance += diff
			
	return distance

def calc_distance_full_amr(l):
	'''Calculates distance between list items in 2 two lists'''
	
	#l needs to start from zero, get lowerst number and substract it from all numbers
	
	distance = 0
	l = [x for x in l if (x[1] != '' and len(x) > 1)]
	
	sorted_l = sorted(l, key = lambda x:x[1])
	
	#calculate difference between where optimal position is (in sorted) and where the item is now
	
	for idx, item in enumerate(l):
		rank_sorted = sorted_l.index(item)
		diff = abs(idx - rank_sorted)
		distance += diff
			
	return distance		


def do_swap(w_list1, w_list2):
	'''Checks if we should swap two list items'''
	
	distance_now  = calc_distance(w_list1 + w_list2)
	distance_swap = calc_distance(w_list2 + w_list1)
	
	
	return distance_now > distance_swap			#true or false		


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


def combine_amrs(validated_old, validated_new, validated_sents, filter_same):
	assert(len(validated_new) == len(validated_sents) == len(validated_old))
	
	new_sents = []
	new_amrs = []
	
	for idx in range(0, len(validated_old)):
		no_var_new = re.sub(r'\((.*?/)', '(', validated_new[idx]).replace('( ', '(')
		no_var_old = re.sub(r'\((.*?/)', '(', validated_old[idx]).replace('( ', '(')
		if validated_old[idx] == validated_new[idx] and filter_same:
			new_sents.append(validated_sents[idx])
			new_amrs.append(no_var_new)
		else:	
			new_sents.append(validated_sents[idx])
			new_sents.append(validated_sents[idx])
			new_amrs.append(no_var_old)
			new_amrs.append(no_var_new)
	
	assert len(new_sents) == len(new_amrs)
	print 'Adding double, new length:', len(new_sents)
	print 'Doubled AMRs: {0}'.format(len(new_sents) - len(validated_old))
	return new_amrs, new_sents	


def check_validity(old_amrs_f, new_amrs_f, sent_amrs):
	'''Check if newly created AMRs are valid'''
	
	new_amrs = [x.strip() for x in open(new_amrs_f,'r')]
	old_amrs = [x.strip() for x in open(old_amrs_f,'r')]
	
	for idx in range(len(old_amrs)):
		while ' )' in old_amrs[idx]:
			old_amrs[idx] = old_amrs[idx].replace(' )',')')		#fix "errors" in annotation
	
	validated_new = []
	validated_old = []
	validated_sents = []
	invalid_new, invalid_length = 0, 0
	
	assert len(new_amrs) == len(old_amrs) == len(sent_amrs)
	
	for idx in range(len(old_amrs)):
		#if len(old_amrs[idx]) != len(new_amrs[idx]):
		if abs(len(old_amrs[idx]) - len(new_amrs[idx])) > 2:
			invalid_length += 1
		elif not validator_seq2seq.valid_amr(new_amrs[idx]):
			invalid_new += 1
		else:											# valid amrs		
			if validator_seq2seq.valid_amr(old_amrs[idx]):
				validated_old.append(old_amrs[idx])
				validated_new.append(new_amrs[idx])
				validated_sents.append(sent_amrs[idx])						
	
	print 'Invalid {0} based on length and {1} AMR-parse'.format(invalid_length, invalid_new)							
	
	assert(len(validated_new) == len(validated_sents) == len(validated_old))
	
	return validated_old, validated_new, validated_sents


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
		if ')' not in p or '(' not in p:				
			if p.count(':') > 2:
				p_split = p.split(':')[1:]
				new_perms = [':' + x.strip() for x in p_split]
				return add_string, new_perms
	
	
	return add_string, permutations			


def get_keep_string(new_parts, level):
	'''Obtain string we keep, it differs for level 1'''
	
	if level > 1:
		keep_string = ':' + ":".join(new_parts[:1])
	else:
		keep_string = ":".join(new_parts[:1])
	search_part = ':' + ":".join(new_parts[1:])
	
	return keep_string, search_part
	

def combine_permutations(permutations, cut_off):
	'''Combine permutations if they exceed the cut-off specified'''
	
	if len(permutations) > cut_off:
		shuffle(permutations)
		permutations = permutations[0:args.cut_off - 1] + [" ".join(permutations[args.cut_off - 1:])]	# just add extra permutations to the last permutation
	
	return permutations

											
def get_permutations(part, level,  sent_amr):	
	part = part[1:] 																			# make life easier by skipping first '(' or ':'
	sent_words = [w.lower() for w in sent_amr.split()]  										# get all words in sentence in lower case
	
	if ':' not in part or (part.count(':') == 1 and ('http:' in part or 'https:' in part)):		# if there is nothing to change then we return
		if level == 1:
			return [part], ''
		else:	
			return [':' + part], ''	

	new_parts 				 = filter_colons(part)												#remove non-arguments that have a colon such as timestamps and websites
	keep_string, search_part = get_keep_string(new_parts, level)
	add_string, permutations = get_add_string(search_part) 
	
	permutations = combine_permutations(permutations, args.cut_off)	
	word_list 	 = matching_words(permutations)													#find the list of lists that contain word-sense pairs
	if len(word_list)!= len(permutations):
		print 'Strange AMR part'
		return permutations, keep_string																		#find best permutation
	else:
		for p in range(len(permutations)):
			for idx in range(len(permutations)-1):
				if do_swap(word_list[idx], word_list[idx+1]):
					permutations[idx], permutations[idx+1] = permutations[idx+1], permutations[idx]
					word_list[idx], word_list[idx+1] = word_list[idx+1], word_list[idx]			
								
		return permutations, keep_string		


def do_string_adjustments(permutations_new, keep_string2):
	add_string = keep_string2 + ' ' + " ".join(permutations_new) + ' '
	
	while add_string.count(')') < add_string.count('('): 			## check if we need to add a parenthesis
		add_string += ')' 											## avoid extra unnecessary space
	
	return add_string


def create_final_line(final_string):
	'''Do final adjustments for line'''
	
	add_to = final_string.replace('  ',' ') .strip()
	while ' )' in add_to:
		add_to = add_to.replace(' )',')')
	
	add_to = fix_paren(add_to)	
	add_to = remove_sense(add_to)
	add_to = add_to.replace('):',') :').replace(' :)',')').replace(': :',':')
	
	return add_to
	
		
def fix_paren(string):
	while string.count('(') > string.count(')'):
		string += ')'
	return string	


def get_best_perm(permutations, keep_str, sent, final_string):
	
	'''This must also be possible recursive'''
	
	
	for indx2, p2 in enumerate(permutations):
		permutations_2, keep_string2 = get_permutations(p2,2, sent)
		
		for indx3, p3 in enumerate(permutations_2):
			permutations_3, keep_string3 = get_permutations(p3,3, sent)
			
			for indx4, p4 in enumerate(permutations_3):
				permutations_4, keep_string4 = get_permutations(p4,4, sent)
			
				for indx5, p5 in enumerate(permutations_4):
					permutations_5, keep_string5 = get_permutations(p5,5, sent)
					
					for indx6, p6 in enumerate(permutations_5):
						permutations_6, keep_string6 = get_permutations(p6,6, sent)
						
						for indx7, p7 in enumerate(permutations_6):
							permutations_7, keep_string7 = get_permutations(p7,7, sent)
							
							for indx8, p8 in enumerate(permutations_7):
								permutations_8, keep_string8 = get_permutations(p8,8, sent)
								
								for indx9, p9 in enumerate(permutations_8):
									permutations_9, keep_string9 = get_permutations(p9,9, sent)
									
									for indx10, p10 in enumerate(permutations_9):
										permutations_10, keep_string10 = get_permutations(p10,10, sent)
										
										for indx11, p11 in enumerate(permutations_10):
											permutations_11, keep_string11 = get_permutations(p11,11, sent)
											
											for indx12, p12 in enumerate(permutations_11):
												permutations_12, keep_string12 = get_permutations(p12,12, sent)
												add_string = do_string_adjustments(permutations_12, keep_string12)
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

									
def process_file_best(amrs, sent_amrs):
	'''Do permutations for best permutation'''
	
	print 'Best permutation'
	
	save_all_amrs = []
	assert len(amrs) == len(sent_amrs)
	for idx, amr in enumerate(amrs):
		if amr.count(':') > 1:		#only try to do something if we can actually permutate					
			permutations, keep_string1 = get_permutations(amr,1, sent_amrs[idx])
			keep_str = '(' + keep_string1 
			final_string = get_best_perm(permutations, keep_str, sent_amrs[idx], keep_str)
			add_to = create_final_line(final_string)
			save_all_amrs.append(add_to)							## add final string + final parenthesis 
		else:
			amr = remove_sense(amr)
			save_all_amrs.append(amr)
	
	for idx, a in enumerate(amrs):
		amrs[idx] = amrs[idx].replace(' )',')')
		amrs[idx] = remove_sense(amrs[idx])
	
	changed_amrs = len(amrs) -  len([i for i, j in zip(amrs, save_all_amrs) if i == j])
	
	print 'Changed {0} out of {1} amrs'.format(changed_amrs, len(amrs))
	
	return save_all_amrs, amrs, changed_amrs


def preprocess(f_path):
	'''Preprocess the AMR file, deleting variables/wiki-links and tokenizing'''
	
	no_wiki_amrs       = delete_wiki(f_path)
	del_amrs 		   = delete_amr_variables(no_wiki_amrs)
	sent_amrs 		   = get_tokenized_sentences(f_path)		# tokenization is already done by the aligned data, so use that
	old_amrs		   = single_line_amrs(del_amrs)				# old amrs with deleted wiki and variables
	
	return no_wiki_amrs, del_amrs, sent_amrs, old_amrs


def write_output(f, old_amrs, new_amrs, sent_amrs):
	
	file_new, file_old, restore_new, restore_old, sent_old, sent_new, double_sent, double_amr = get_filenames(f, args.f, '.new','.old','.restore','.old.sent','.new.sent')
		
	write_to_file(old_amrs, file_old)
	write_to_file(new_amrs, file_new)
	write_to_file(sent_amrs, sent_old)
	
	restore_amrs(file_new, restore_new)		# both also write to file
	restore_amrs(file_old, restore_old)
	
	validated_old, validated_new, validated_sents = check_validity(restore_old, restore_new, sent_amrs)
	
	write_to_file(validated_old, restore_old)
	write_to_file(validated_new, restore_new)
	write_to_file(validated_sents, sent_new)

	if args.double:
		validated_combined_amrs, validated_combined_sents = combine_amrs(validated_old, validated_new, validated_sents, filter_same = True)		# double amrs!	
		write_to_file(validated_combined_amrs, double_amr)
		write_to_file(validated_combined_sents, double_sent)
	

if __name__ == '__main__':

	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.amr_ext):
				print '\n',f
				f_path = os.path.join(root,f)
				no_wiki_amrs, del_amrs, sent_amrs, old_amrs  = preprocess(f_path)
				new_amrs, old_amrs, changed_amrs = process_file_best(old_amrs, sent_amrs)
				write_output(f, old_amrs, new_amrs, sent_amrs)
			
	if args.cleanup:
		os.system('rm {0}*.txt.new*'.format(args.f.strip()))
		os.system('rm {0}*.txt.old*'.format(args.f.strip()))		
		
