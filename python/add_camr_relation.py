import os
import sys
import argparse
import re
from Levenshtein import jaro

'''Scripts that adds CAMR relation of a word as a feature'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="POS-tagged sentence file that needs feature")
parser.add_argument("-a", required=True, type=str, help="File with the aligned CAMR parses")
parser.add_argument("-o", required=True, type=str, help="Output-file with CAMR-tagged sentences")
args = parser.parse_args()


def remove_pos_tags(sent):
	no_pos_sent = []
	
	for x in sent.split():
		if len(x) < 2 or '|' not in x:
			no_pos_sent.append(x)
		else:
			add = "|".join(x.split('|')[0:-1]).lower()
			no_pos_sent.append(add)
			
	sent_lower = " ".join(no_pos_sent)
	
	return sent_lower


def check_sents(sent, align_sent):
	al_sent = align_sent[2:].split()								#remove initial '# '
			
	sent_lower = remove_pos_tags(sent)								#remove postag and do lowercase				
	aligned_sent = ["_".join(x.split('_')[0:-1]) for x in al_sent]	#remove word_number
	final_aligned =  " ".join(aligned_sent)							#join back to sent
	if jaro(final_aligned, sent_lower) > 0.90:						#some small changes might occur, not a problem if jaro is high enough
		return True
	else:
		return False


def get_alignments(amr, sent):
	
	split_sent = sent.split()
	split_amr = amr.split()
	prev_rel = None
	
	for item in split_amr:
		if len(item) > 2 and item[0] == ':' and item[1].isalpha() and item[2].isalpha():
			prev_rel = item.split('~')[0].replace('arg','ARG')		#remove occasional sense from relation
		elif not item.startswith(':') and '~e.' in item:
			num_str = re.findall(r'~e\.([\d]+)', item)
			assert len(num_str) == 1
			num = int(num_str[0])
			rel = item.split('~')[0].replace('"','')
			if not prev_rel:
				split_sent[num] += '|:head'
			else:
				split_sent[num] += ('|' + prev_rel)
	
	return " ".join(split_sent)				
			

def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()					
			
		
if __name__ == '__main__':
	sents = [x.strip() for x in open(args.f,'r')]
	
	inf = []
	snt_idx = 0
	tagged_sents = []
	
	for line in open(args.a,'r'):
		if line.startswith('# '):
			inf.append(line)
		elif line.strip():
			inf.append(line)
		else:		
			assert len(inf) == 2
			if check_sents(sents[snt_idx], inf[0]):		#if true the sentences perfectly align
				tagged_sent = get_alignments(inf[1], sents[snt_idx])
				tagged_sents.append(tagged_sent)
			else:
				raise ValueError('Sentences are not aligned!')	
			
			inf = []
			snt_idx += 1
	
	assert(len(sents) == len(tagged_sents))
	write_to_file(tagged_sents, args.o)	
			
