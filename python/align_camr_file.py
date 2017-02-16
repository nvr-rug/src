import os
import sys
import argparse
import re
from Levenshtein import jaro

'''Scripts that adds CAMR relation of a word as a feature'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="sentence file that needs feature")
parser.add_argument("-c", required=True, type=str, help="File with CAMR parses")
parser.add_argument("-a", required=True, type=str, help="AMR tf file")
args = parser.parse_args()

if __name__ == '__main__':
	sents_orig = [x.strip() for x in open(args.f,'r')]
	tf_amrs = [x.strip() for x in open(args.a,'r')]
	
	parse_dict = {}
	
	cur_amr = []
	
	for line in open(args.c,'r'):
		if line.startswith('# ::tok'):
			cur_line = line.replace('# ::tok','').strip()
		elif line.startswith('# ::'):
			continue
		elif not line.strip():
			cur_amr_line = " ".join(cur_amr)
			find_line = cur_line.replace(' ','')
			repl_line = cur_line.replace('-RRB-','').replace('-LRB-','').replace('-LLB-','').replace('-RLB-','')
			regex_line_1 = re.sub(r'\W+', '', cur_line).lower()
			regex_line_2 = re.sub(r'\W+', '', repl_line).lower()
			parse_dict[cur_line] = [cur_amr, cur_line]
			parse_dict[find_line] = [cur_amr, cur_line]
			parse_dict[regex_line_1] = [cur_amr, cur_line]
			parse_dict[regex_line_2] = [cur_amr, cur_line]
			parse_dict[repl_line] = [cur_amr, cur_line]
			cur_amr = []
		else:
			cur_amr.append(line.rstrip())
	
	new_camr = []
	keep_sents = []
	keep_tf = []
	camr_one_line = []
	
	for idx, s in enumerate(sents_orig):
		if len(s.split()) == 1:
			if s.strip() == '.' or s.strip() == 'April':		#these sentences gave weird bugs in the aligner
				continue
		else:		
			if idx % 200 == 0 and idx != 0:
				with open(args.c + '.lin','w') as out_f:
					for l in new_camr:
						out_f.write(l.rstrip() + '\n')
				out_f.close()
				
				with open(args.a + '.lin','w') as out_f:
					for l in keep_tf:
						out_f.write(l.strip() + '\n')
				out_f.close()
				
				with open(args.f + '.lin','w') as out_f:
					for l in keep_sents:
						out_f.write(l.strip() + '\n')
				out_f.close()
				
				with open(args.c + '.lin.ol','w') as out_f:
					for l in camr_one_line:
						out_f.write(l.strip() + '\n')
				out_f.close()
			
			s2 = s.replace('-RRB-','').replace('-LRB-','').replace('-LLB-','').replace('-RLB-','')
			s3 = re.sub(r'\W+', '', s).lower()
			s4 = re.sub(r'\W+', '', s2).lower()
			
			if s in parse_dict:
				new_camr.append('# ::tok ' + parse_dict[s][1])
				new_camr += parse_dict[s][0]
				new_camr.append('')
				keep_sents.append(s)
				keep_tf.append(tf_amrs[idx])
				camr_one_line.append(" ".join(" ".join(parse_dict[s][0]).split()))
				
			elif s2 in parse_dict:
				new_camr.append('# ::tok ' + parse_dict[s2][1])
				new_camr += parse_dict[s2][0]
				new_camr.append('')
				keep_sents.append(s)
				keep_tf.append(tf_amrs[idx])
				camr_one_line.append(" ".join(" ".join(parse_dict[s2][0]).split()))
				
			elif s3 in parse_dict:
				new_camr.append('# ::tok ' + parse_dict[s3][1])
				new_camr += parse_dict[s3][0]
				new_camr.append('')
				keep_sents.append(s)
				keep_tf.append(tf_amrs[idx])
				camr_one_line.append(" ".join(" ".join(parse_dict[s3][0]).split()))
				
			elif s4 in parse_dict:
				new_camr.append('# ::tok ' + parse_dict[s4][1])
				new_camr += parse_dict[s4][0]
				new_camr.append('')
				keep_sents.append(s)
				keep_tf.append(tf_amrs[idx])
				camr_one_line.append(" ".join(" ".join(parse_dict[s4][0]).split()))
				
			else:
				for key in parse_dict:
					if jaro(key, s4) > 0.80:
						new_camr.append('# ::tok ' + parse_dict[key][1])
						new_camr += parse_dict[key][0]
						new_camr.append('')
						keep_sents.append(s)
						keep_tf.append(tf_amrs[idx])
						camr_one_line.append(" ".join(" ".join(parse_dict[key][0]).split()))
						break
	
	with open(args.c + '.lin','w') as out_f:
		for l in new_camr:
			out_f.write(l.rstrip() + '\n')
	out_f.close()
	
	with open(args.a + '.lin','w') as out_f:
		for l in keep_tf:
			out_f.write(l.strip() + '\n')
	out_f.close()
	
	with open(args.f + '.lin','w') as out_f:
		for l in keep_sents:
			out_f.write(l.strip() + '\n')
	out_f.close()
	
	with open(args.c + 'lin.ol','w') as out_f:
		for l in camr_one_line:
			out_f.write(l.strip() + '\n')
		out_f.close()
				

