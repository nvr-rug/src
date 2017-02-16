import os, sys, json, re
from random import shuffle

order_file = sys.argv[1]

def dump_json_dict(d, f_name):	
	with open(f_name, 'w') as fp:
		json.dump(d, fp)
	fp.close()

def percentage_first(order, ident):
	total_first, total, occurences = 0, 0, 0
	
	other_first = []
	
	for key in order:
		if ident in key and len(key.split()) > 1:
			split_keys = key.split()
			if ident in split_keys:
				idx = split_keys.index(ident)
				if idx == len(split_keys) - 1:	#last
				#if idx == 0:					#first
					total_first += order[key]
				else:
					other_first.append(split_keys[0])	
				total += order[key]
				occurences += 1
	
	if occurences < 10 or not other_first:
		return False, False, False, False, False
	else:
		most_common = max(set(other_first), key=other_first.count)
		pct_max = round(float(other_first.count(most_common)) / float(len(other_first)),2)
		return round(float(total_first) / float(total), 2), total_first, total, most_common, pct_max
				

def print_stats(all_keys, order):			
	pct_dict = {}
	
	for k in all_keys:
		pct, total_first, total, most_common, pct_max = percentage_first(order, k)
		if pct:
			pct_dict[k] = [float(pct), total_first, total, most_common, pct_max]

	for d in sorted(pct_dict.items(), key = lambda x : float(x[1][0]), reverse = True):
		print d[0], d[1][0], d[1][2],'soms', d[1][3], d[1][4]		


def define_order(all_keys, order):
	order_dict = {}
	list_args = []
	
	print 'len:', len(all_keys)
	
	for idx, key in enumerate(all_keys):
		if key not in list_args:
			list_args.append(key)
		if idx % 20 == 0:
			print 'idx', idx
		for key2 in all_keys:
			comb_key = key + ' ' + key2
			if key != key2 and comb_key not in order_dict:
				first, non_first = 0, 0
				for k in order:
					split_keys = k.split()
					if key in split_keys and key2 in split_keys:
						if split_keys.index(key) > split_keys.index(key2):
							non_first += order[k]
						else:
							first += order[k]
				
				comb_key_rev = key2 + ' ' + key
				order_dict[comb_key] = [first, non_first]
				order_dict[comb_key_rev] = [non_first, first]
	
	return order_dict, list_args						 	

def do_swap_order(p1, p2, order_dict):
	
	arg_p1 = p1.split()[0].split('~')[0]		#also remove sense
	arg_p2 = p2.split()[0].split('~')[0]
	comb_arg = arg_p1 + ' ' + arg_p2
	
	if arg_p1[0] != ':' or arg_p2[0] != ':':	#something weird is going with the data, don't swap
		return False
	elif arg_p1 == arg_p2:						#same argument, don't swap
		return False
	elif comb_arg not in order_dict:			#we don't recognize one of the arguments, don't swap
		print 'Combination unknown:', comb_arg
		return False
	elif order_dict[comb_arg][0] < order_dict[comb_arg][1]: #arg1 more often occurs after arg2, so swap	
		return True
	else:
		return False
			
if __name__ == "__main__":
	with open(order_file, 'r') as fp:	# load in dictionary
		order = json.load(fp)

	all_keys = []

	for key in order:
		list_keys = key.split()
		for l in list_keys:
			if l not in all_keys:
				all_keys.append(l)
	
	#print_stats(all_keys)
	res_dict, list_args = define_order(all_keys, order)
	
	dump_json_dict(res_dict, '/home/p266548/Documents/amr_Rik/defined_order_dict.txt')

	
	#order based on train data
	
	shuffle(list_args)
	
	for idx in range(len(list_args) * 10):
		for i in range(len(list_args) - 1):
			if do_swap_order(list_args[i], list_args[i+1], res_dict):
				list_args[i], list_args[i+1] = list_args[i+1], list_args[i]
	
	final_ordered_dict = {}
	
	for idx, i in enumerate(list_args):
		final_ordered_dict[i] = idx
	
	dump_json_dict(final_ordered_dict, '/home/p266548/Documents/amr_Rik/sorted_order_dict.txt')
	
	#alphabetical order
	
	list_args = [x.lower() for x in list_args]
	
	for idx, item in enumerate(list_args):		#silly hack to sort ARG0-of and ARG1-of after ARG2, ARG3, ARG4 etc
		list_args[idx] = re.sub(r'arg(\d)-of',r'arga\1-of',item)
	
	alphabetical_list = sorted(list_args)		#this sorts alphabetically
	
	alphabetical_list = [x.replace('arga','arg').replace('arg','ARG') for x in alphabetical_list] #and change it back
	
	alpha_dict = {}
	
	for idx, i in enumerate(alphabetical_list):
		alpha_dict[i] = idx
		print i, idx
	
	dump_json_dict(alpha_dict, '/home/p266548/Documents/amr_Rik/alphabetical_order_dict.txt')	
	
	
		
