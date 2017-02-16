import os
import sys
reload(sys)
import argparse
import re

'''Script that only keeps the words of an AMR (plus some structure words probably) - overwrites files!
   Data is assumed to be in single-line format, without variables/wiki-links/etc'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="AMRs folder")
parser.add_argument("-output_ext", default = '.tf', type=str, help="Extension of output")
args = parser.parse_args()


if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:							
			f_path = os.path.join(root, f)		
			if f.endswith(args.output_ext) and 'char' not in f :
				new_lines = []
				for line in open(f_path,'r'):
					l = re.sub(r':[^ ]+','',line).replace(')','').replace('(','').replace('"','')
					l = re.sub(r'([a-zA-Z]+)-[\d]+',r'\1',l)
					l = " ".join(l.split())
					new_lines.append(l.strip())

				with open(f_path,'w') as out_f:						
					for n in new_lines:
						out_f.write(n.strip() + '\n')
