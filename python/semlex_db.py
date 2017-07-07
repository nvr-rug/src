#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Script that gets the semlex zardoz database'''

import re,sys, argparse, os, subprocess, json, random
import pmb
reload(sys)
from collections import Counter

#parser = argparse.ArgumentParser()
#parser.add_argument("-f1", required = True, type=str, help="First file with AMRs")
#args = parser.parse_args()

d = {}

config = pmb.read_config()
with pmb.DB(config) as db:
	query = """SELECT * FROM `gsb_semlex_entry` WHERE 1"""
	res = db.get(query)

for item in res:
	if item[0] not in d:
		d[item[0]] = item[1]
	else:
		print 'Double?'	

count_d = {}

with pmb.DB(config) as db:
	query = """SELECT lemma, cat, semtag, entry_id FROM `gsb_semlex_occurrence` WHERE 1"""
	res = db.get(query)

for item in res:
	check = item[0] + ' ' + item[1] + ' ' + item[2]
	add = d[item[3]]
	if check not in count_d:
		count_d[check] = [add]
	else:
		count_d[check].append(add)

for key in count_d:
	if len(set(count_d[key])) == 1:
		pass
		#print 'One option'
	else:
		#print 'More options'
			
		c = Counter(count_d[key]).most_common()
		print '\nFor {0}:\n'.format(key.encode('utf-8').strip())
		for k in c:
			print k[0], k[1]
			
			
