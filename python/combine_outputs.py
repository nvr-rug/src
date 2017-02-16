import os
import sys
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("-p", required=True, type=str, help="directory that contains produced amrs / sentences")
parser.add_argument("-g", required=True, type=str, help="directory that contains gold amrs / sentences")
parser.add_argument("-gold_ext", default = '.txt',  required=False, type=str, help="Input extension (default .sent))")
parser.add_argument("-prod_ext", default = '.seq.amr',  required=False, type=str, help="Input extension (default .sent))")
parser.add_argument("-uniq_id", required=True,  required=False, type=str, help="Needs uniq ID so that we can test multiple eval scripts in parallel")

args = parser.parse_args()

if __name__ == '__main__':
	total_gold = []
	total_prod = []
	
	for root1, dirs1, files1 in os.walk(args.p):
		for f1 in files1:
			for root2, dirs2, files2 in os.walk(args.g):
				for f2 in files2:
					if f1.endswith(args.prod_ext) and f2.endswith(args.gold_ext):
						match_p = f1.split('-')[-1].split('.')[0]
						match_g = f2.split('-')[-1].split('.')[0]
						match_part_p = f1.replace(match_p,'combined')
						match_part_g = f1.replace(match_g,'combined')
						if match_p == match_g:
							prod_amrs = [x.rstrip() for x in open(os.path.join(root1, f1))]
							gold_amrs = [x.rstrip() for x in open(os.path.join(root2, f2))]
							total_prod += prod_amrs
							total_gold += gold_amrs		
	
	with open(args.p + match_part_p,'w') as out_f:
		for p in total_prod:
			out_f.write(p.strip() + '\n')
	out_f.close()			
	
	with open(args.p + match_part_g + '_' + uniq_id,'w') as out_f:
		for g in total_gold:
			out_f.write(g.rstrip() + '\n')
	out_f.close()
