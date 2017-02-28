import os
import sys
import argparse
import re
import json

'''Script that saves bio-data Wiki links'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Train-file with AMRs")
args = parser.parse_args()

def get_name_from_amr_line(line):
	'''Takes an AMR-line with a :name, returns the full name as a string'''
	name_parts = re.findall(':op[0-9]+ ".*?"', line)
	name_parts = [x[6:-1] for x in name_parts] # Remove garbage around name parts
	return ' '.join(name_parts)

def get_wiki_item(line):
	if ':wiki -' in line:
		return '-'
	else:
		wiki_name = re.findall(':wiki ".*?"', line)
		
		wiki = wiki_name[0].split()[1].replace('"','')
		return wiki
		
#def add_to_dict(d, key, value):
	#if key in d:
		#if value == '-':
			#pass
		#elif not d[key] == value:
			#if d[key] == '-':
				#d[key] = value	#override no wiki value
			#else:
				#print 'Should not happen, but:\n {0} vs {1} for key {2}'.format(d[key], value, key)
	#else:
		#d[key] = value
	#return d				

def add_to_dict(d, key, value):
	if key in d:
		d[key].append(value)
	else:
		d[key] = [value]
	
	return d	


def most_common(lst):
    return max(set(lst), key=lst.count)


if __name__ == '__main__':
	prev_wiki = False
	
	wiki_dict = {}
	name_dict = {}
	
	for idx, line in enumerate(open(args.f,'r')):
		if prev_wiki:
			if ':name' in line:
				name = get_name_from_amr_line(line)
				#print prev_wiki, name
				wiki_dict = add_to_dict(wiki_dict, name, prev_wiki)
				prev_wiki = False
			else:
				pass
				#print 'Strange', idx	
		
		elif ':wiki' in line:
			if ':name' in line.split(':wiki')[1]:
				wiki_item = get_wiki_item(line)
				name = get_name_from_amr_line(line)
				wiki_dict = add_to_dict(wiki_dict, name, wiki_item)
			else:
				prev_wiki = get_wiki_item(line)	
		else:
			prev_wiki = False
	
	for idx, line in enumerate(open(args.f,'r')):
		if ':name' in line:
			name = get_name_from_amr_line(line)
			if name in name_dict:
				name_dict[name] += 1
			else:
				name_dict[name] = 1
	
	#for name in name_dict:
		#if name in wiki_dict:
			#wiki_list = [x for x in wiki_dict[name] if x != '-']
			#if len(set(wiki_list)) > 1:
				#print 'Name {2} occurs {0} times, Wikified {1} times'.format(name_dict[name], len(wiki_dict[name]), name)
				#print set(wiki_list)
			#else:	
			#	if len(wiki_dict[name]) != name_dict[name]:
			#		print 'Name {2} occurs {0} times, Wikified {1} times'.format(name_dict[name], len(wiki_dict[name]), name)
					#if len(wiki_dict[name]) > 10:
						#print wiki_dict[name][0:10]
					#else:
						#print wiki_dict[name]
					#print '\n'		
			
	for name in name_dict:
		if name in wiki_dict:
			if (float(len(wiki_dict[name])) /  float(name_dict[name])) < 0.50:		#delete that goes wrong more than 50% of the time
				#print 'delete', len(wiki_dict[name]), name_dict[name]
				del wiki_dict[name]
	
	for key in wiki_dict:
		wiki_dict[key] = most_common(wiki_dict[key])						
	
	with open('/home/p266548/Documents/amr_Rik/sem_eval_testdata/wiki_dict.txt','w') as out_f:
		json.dump(wiki_dict, out_f)				
		
