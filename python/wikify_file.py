import os
import sys
import argparse
import re
import wikification_seq2seq
import validator_seq2seq

'''Wikifies an AMR-file (input on one line with variables)'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="AMR-file to be wikified")
parser.add_argument("-s", required=True, type=str, help="Sent file that is needed for the Wikification")
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f, 'w') as out:
		for l in lst:
			out.write(l.strip() + '\n')
	out.close()


def get_default_amr():
	default='(w / want-01 :ARG0 (b / boy) :ARG1 (g / go-01 :ARG0 b))'
	return default


def check_valid(restore_file, rewrite):
	'''Checks whether the AMRS in a file are valid, possibly rewrites to default AMR'''
	
	idx = 0
	warnings = 0
	all_amrs = []
	for line in open(restore_file,'r'):
		idx += 1
		if not validator_seq2seq.valid_amr(line):
			print 'Error or warning in line {0}, write default\n'.format(idx)
			warnings += 1
			all_amrs.append(get_default_amr())		## add default when error
		else:
			all_amrs.append(line)	
	
	if warnings == 0:
		print 'No badly formed AMRs!\n'
	elif rewrite:
		print 'Rewriting {0} AMRs with error to default AMR\n'.format(warnings)
		write_to_file(all_amrs, restore_file)
				
	else:
		print '{0} AMRs with warning - no rewriting to default\n'.format(warnings)



def add_wikification(in_file, sent_file):
	wiki_file = in_file + '.wiki'
	
	if not os.path.isfile(wiki_file):
		wikification_seq2seq.wikify_pipeline_output(in_file, 'dbpedia', sent_file, '')	
		num_sents = len([x for x in open(sent_file,'r')])	#for checking whether Wikification succeeded
		num_wiki = len([x for x in open(wiki_file,'r')])
		
		assert (num_sents == num_wiki)
		print 'Validating...'
		
		check_valid(wiki_file, True)
		
	else:
		print 'Wiki file already exists, skipping...'


if __name__ == "__main__":
	add_wikification(args.f, args.s)
