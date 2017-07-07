#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Takes AMR output from the pipeline, and performs wikification
in a post-processing step. Can also be run on the gold standard data,
then it evaluates wikification performance. Currently uses the DBPedia
Spotlight webservice, rather than a Spotlight service running locally.
'''

from time import sleep
import re, os, requests, argparse
from bs4 import BeautifulSoup
import sys
reload(sys)

# Get wikification from DBpedia spotlight
def get_wiki_from_spotlight_by_name(spotlight, name):
	'''Given the spotlight output, and a name string, e.g. 'hong kong'
	returns the wikipedia tag assigned by spotlight, if it exists, else '-'.'''
	# Check if this name has already been wikified before
	actual_found = 0
	#print 'name:', name
	parsed_spotlight = BeautifulSoup(spotlight.text, 'lxml')
	for wiki_tag in parsed_spotlight.find_all('a'):
		#print '\t', wiki_tag.string
		if wiki_tag.string.lower() == name.lower():
			actual_found += 1
			#print wiki_tag.get('href').split('/')[-1]
			return wiki_tag.get('href').split('/')[-1], actual_found
	# If nothing found, try to match based on prefixes, e.g. match the name Estonia to the tag for 'Estonian'
	for wiki_tag in parsed_spotlight.find_all('a'):
		if wiki_tag.string.lower()[:len(name)] == name.lower():
			actual_found += 1
			return wiki_tag.get('href').split('/')[-1], actual_found
#	for wiki_tag in parsed_spotlight.find_all('a'):
#		if re.match(wiki_tag.string.lower(), name.lower()):
#			return wiki_tag.get('href').split('/')[-1]
#	if ' ' not in name: # If it's a single word, return the word itself
#		return name
	
	return '-', actual_found

# Get wikification from Illinois Wikifier
def get_wiki_from_illinois_by_name(name, sentence, sentenceID, wikified_text, memory):
#	print 'sentence: %s' % sentence
#	print 'currName: %s' % name
	# Try to match string exactly (regardless of case, though)
	for wiki_tag in wikified_text[sentenceID].find_all('a'):
		if wiki_tag.string.lower() == name.lower():
			return wiki_tag.get('href').split('/')[-1]
	# If nothing found, check if this name has already been wikified before
	if name in memory:
		return memory[name]
	# If still nothing found, try to match based on prefixes, e.g. match the name Estonia to the tag for 'Estonian'
	for wiki_tag in wikified_text[sentenceID].find_all('a'):
		if wiki_tag.string.lower()[:len(name)] == name.lower():
			return wiki_tag.get('href').split('/')[-1]
	return '-'

def load_wikified_text(indir, docName):
	suffix = '.txt.textonly.wikification.tagged.flat.html'
	infile = open(indir + docName + suffix, 'r')
	indata = infile.read()
	indata = indata.split('<br>')
	parsed_sentences = []
	for sentence in indata:
		parsed_sentences.append(BeautifulSoup(sentence, 'lxml'))
	return parsed_sentences

def get_name_from_amr_line(line):
	'''Takes an AMR-line with a :name, returns the full name as a string'''
	name_parts = re.findall(':op[0-9]+ ".*?"', line)
	name_parts = [x[6:-1] for x in name_parts] # Remove garbage around name parts
	return ' '.join(name_parts)

def wikify_pipeline_output(in_file, wikifier, in_sents, f_out):
	'''Takes .amr-files as input, outputs .amr.wiki-files
	with wikification using DBPedia Spotlight. Specify whether
	to use DBpedia or Illinois wikifier.'''

	# Wikify all files in input directory
	
	sentences = [x.strip() for x in open(in_sents,'r')]
	all_found = 0
	unicode_errors = 0
	
	with open(in_file, 'r') as infile:
		with open(in_file + '.wiki', 'w') as outfile:
			foundName = False
			foundWiki = False
			currName = '' # String to contain the parts of names found
			#wiki_memory = {} # Store already wikified names and their wikis for lookup
			
			if wikifier.lower() == 'dbpedia':
				spotlight = '' # Spotlight results
			else:
				raise ValueError("Only dbpedia works in this script")	
			
			for idx, line in enumerate(infile):
				#print 'Idx {0}'.format(idx)
				sentence = sentences[idx]
				#if ':name' not in line:
					#outfile.write(line)
					#continue
						
				if wikifier.lower() == 'dbpedia':
					# Spotlight raises an error if too many requests are posted at once
					success = False
					while not success:
						try:
							#spotlight = requests.post("http://spotlight.sztaki.hu:2222/rest/annotate", data = {'text':sentence, 'confidence':0.3})
							#spotlight = requests.post("http://model.dbpedia-spotlight.org:2222/rest/annotate", data = {'text':sentence, 'confidence':0.3})
							spotlight = requests.post("http://model.dbpedia-spotlight.org/en/annotate", data = {'text':sentence, 'confidence':0.3})
							spotlight.encoding = 'utf-8'
						except requests.exceptions.ConnectionError:
							print 'sleeping a bit (spotlight overload)'
							sleep(0.1)
							continue
						success = True
						
				if sentence:
					name_split = line.split(':name')
					#print name_split
					for name_idx in range(1, len(name_split)):	  # skip first in split because name did not occur there yet
						name = get_name_from_amr_line(name_split[name_idx])
						#print str(idx), name
						if name != '':
							wiki_tag, actual_found = get_wiki_from_spotlight_by_name(spotlight, name)
							all_found += actual_found
							if wiki_tag != '-': # Only add when we found an actual result
								do_something = 1
								name_split[name_idx-1] += ':wiki "' + wiki_tag + '" '
							#paren_split = name_split[name_idx].split(')')
							#paren_split[0] += ' :wiki "' + wiki_tag + '"'
							#name_split[name_idx] = ")".join(paren_split)
							
							
								
					try:
						wikified_line = ":name".join(name_split).strip().encode('utf-8')
					except:	#unicode error
						unicode_errors += 1
						wikified_line = line.strip()
						
					outfile.write(wikified_line + '\n')
	#f_out.write('\t\tFound {0} Wiki instances\n'.format(all_found))
	#f_out.write('\t\t{0} Unicode errors\n'.format(unicode_errors))				
						
					#if foundName:
						#if ':op' in line:
##									print get_name_from_amr_line(line)
							#if currName:
								#currName += ' ' + get_name_from_amr_line(line)
							#else:
								#currName = get_name_from_amr_line(line)
##									print 'currName: %s' % currName
							#if ')' in line:
								#if preExistingWiki:
									#wiki_tag = preExistingWiki
									#preExistingWiki = ''
								#elif wikifier.lower() == 'dbpedia':
									#wiki_tag = get_wiki_from_spotlight_by_name(spotlight, currName, wiki_memory)
				
								#if wiki_tag != '-': # Store found wiki tag in memory
									#wiki_memory[currName] = wiki_tag
##										print line[:line.find(')') + 1],
##										print ':wiki "%s"' % wiki_tag,
##										print line[line.find(')') + 1:]
								#try:
									#outfile.write(line[:line.find(')') + 1] + ' :wiki "%s" ' % \
										#wiki_tag.encode('utf-8') + line[line.find(')') + 1:])
								#except:
									#outfile.write(line)		
								#foundName = False
								#currName = ''
							#else:
								#outfile.write(line)

def evaluate_on_gold_standard(input_dir, wikifier):
	'''Takes .txt files containing AMRs from the AMR corpus,
	performs wikification and compares found wiki's to the gold
	standard. Outputs wikification accuracy to screen'''
	# Hack to make it work with a single file, rather than a directory
	if os.path.isfile(input_dir):
		input_file_list = [input_dir]
		input_dir = './'
	else:
		input_dir += '/'
		input_file_list = os.listdir(input_dir)
	# Wikify all files in input directory
	num_correct_wiki = 0.0
	num_correct_nowiki = 0.0
	num_wrong = 0.0
	num_missing = 0.0
	for infilename in input_file_list:
		if re.search('\.txt$', infilename):
			with open(input_dir + infilename, 'r') as infile:
				foundWiki = False
				currName = '' # String to contain the parts of names found
				sentence = '' # The tokenized sentence
				sentenceID = -1
				if wikifier.lower() == 'dbpedia':
					spotlight = '' # Spotlight results
				if wikifier.lower() == 'illinois':
					docName = infilename.split('/')[-1][:-4]
					wikified_text_dir = 'working/WikifiedTexts/no_inference/'
					wikified_text = load_wikified_text(wikified_text_dir, docName)
				wiki_memory = {} # Store already wikified names and their wikis for lookup
				for line in infile:
					if line[0] == '#':
						if re.search('^# ::snt ', line):
							sentence = line.strip()[8:]
							sentenceID += 1
							if wikifier.lower() == 'dbpedia':
								spotlight = requests.post("http://spotlight.sztaki.hu:2222/rest/annotate",
									data = {'text':sentence, 'confidence':0.3})
					elif not line.strip():
						sentence = ''
					elif sentence:
						if ':wiki' in line:
							try: # Extract gold-standard wikification with non-greedy matching
								gold_wiki = re.findall(':wiki ".*?"', line)[0]
								gold_wiki = gold_wiki.decode('iso-8859-1')
							except IndexError:
								gold_wiki = ':wiki "-"'
							if ':name' in line:
								currName = get_name_from_amr_line(line)
							else:
								foundWiki = True
						if foundWiki and ':name' in line:
							currName = get_name_from_amr_line(line)
							foundWiki = False
						if currName:
							if wikifier.lower() == 'dbpedia':
								wiki_tag = get_wiki_from_spotlight_by_name(spotlight, currName, wiki_memory)
							if wikifier.lower() == 'illinois':
								wiki_tag = get_wiki_from_illinois_by_name(currName, sentence, sentenceID, \
									wikified_text, wiki_memory)
							if wiki_tag != '-':
								wiki_memory[currName] = wiki_tag
							my_wiki = ':wiki "%s"' % (wiki_tag)
#							print sentence
#							print 'currName: %s' % currName
#							print 'mine: %s' % my_wiki
#							print 'gold: %s' % gold_wiki
							if my_wiki == gold_wiki:
								if my_wiki == ':wiki "-"':
									num_correct_nowiki += 1
								else:
									num_correct_wiki += 1
							else:
								if my_wiki == ':wiki "-"':
									num_missing += 1
								else:
									num_wrong += 1
							currName = ''
				print num_correct_wiki, num_correct_nowiki, num_wrong, num_missing
				tp = num_correct_wiki
				fp = num_wrong
				tn = num_correct_nowiki
				fn = num_missing
				precision = tp/(tp+fp)*100
				recall = 100*tp/(tp+fn)
				accuracy = 100*(tp+tn)/(tp+tn+fn+fp)
				Fscore = 2*precision*recall/(precision+recall)
				print 'For document %s, accuracy is %05.2f, precision is %05.2f, recall is %05.2f and F-score is %05.2f' % \
					(infilename, accuracy, precision, recall, Fscore)

def main(input_dir, evaluate, wikifier):
	if evaluate:
		evaluate_on_gold_standard(input_dir, wikifier)
	else:
		wikify_pipeline_output(input_dir, wikifier)

if __name__ == '__main__':
	# Parse input arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('input_dir', type=str, help='Path to a single file, or a directory containing either Boxer-produced AMRs for wikification, or gold-standard AMRs for evaluation')
	parser.add_argument('-w', '--wikifier', help = 'Specify wikifier to use, either "illinois" or "dbpedia"', type=str, default='dbpedia')
	parser.add_argument('-e', '--evaluate', help = 'If this flag is given, the script assumes gold-standard AMR formatting, and evaluates wikification performance', dest = 'evaluate', action = 'store_true')
	args = parser.parse_args()
	main(args.input_dir, args.evaluate, args.wikifier)
