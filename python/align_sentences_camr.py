import os
import sys
import argparse
import re
from Levenshtein import jaro
import validator_seq2seq

'''Add AMR if sentence was not filtered in the first place'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="AMR-file")
parser.add_argument("-s", required=True, type=str, help="Sentence file")
parser.add_argument("-o", required=True, type=str, help="Output file")
args = parser.parse_args()

if __name__ == '__main__':
	
	sents = [x.strip() for x in open(args.s,'r')]
	
	all_amrs = []
	cur_amr = []
	for line in open(args.f,'r'):
		if line.startswith('# ::snt'):
			cur_sent = " ".join(line.split()[2:])
			
		elif not line.strip():
			cur_amr_line = " ".join(cur_amr)
			#if validator_seq2seq.valid_amr(cur_amr_line):
			all_amrs.append([cur_sent, cur_amr])
			cur_amr = []
			#else:
			#	print 'Restore made this AMR invalid'	
		else:
			cur_amr.append(line)	
	
	print 'Total AMRs {0} Total sents {1}'.format(len(all_amrs) / 2, len(sents))
	
	
	amr_idx = 0
	sent_idx = 0
	prev_yes = False
	
	with open(args.o, 'w') as out_f:
		for idx, s in enumerate(sents):
			compare_sent = re.sub(r'\W+', '', s).lower()
			amr_sent = re.sub(r'\W+', '', all_amrs[amr_idx][0]).lower()
			
			#print 'Compare:'
			#print s
			#print all_amrs[amr_idx][0],'\n'
			
			while jaro(compare_sent, amr_sent) < 0.83:
				amr_idx += 1
				amr_sent = re.sub(r'\W+', '', all_amrs[amr_idx][0]).lower()
			
			sent_idx += 1
			out_f.write('# ::id sent ' + str(sent_idx) + '\n')
			out_f.write('# ::snt' + ' ' + all_amrs[amr_idx][0].strip() + '\n')
			for l in all_amrs[amr_idx][1]:
				out_f.write(l.rstrip() + '\n')
			out_f.write('\n')
			
			## succes, try next AMR as well for this sentence (since they doubled)
			amr_idx += 1
			compare_sent = re.sub(r'\W+', '', s).lower()
			amr_sent = re.sub(r'\W+', '', all_amrs[amr_idx][0]).lower()
			
			#print 'Compare:'
			#print s
			#print all_amrs[amr_idx][0],'\n'
			
			if jaro(compare_sent, amr_sent) > 0.82:
				sent_idx += 1
				out_f.write('# ::id sent ' + str(sent_idx) + '\n')
				out_f.write('# ::snt' + ' ' + all_amrs[amr_idx][0].strip() + '\n')
				for l in all_amrs[amr_idx][1]:
					out_f.write(l.rstrip() + '\n')
				out_f.write('\n')
				
			
	out_f.close()			
		
