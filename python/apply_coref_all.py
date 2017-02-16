import sys
import re
import argparse
import os
import validator_seq2seq

'''Script that adds coreferents back in produced AMRs'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Root folder to check for files")
parser.add_argument("-input_ext", default = '.restore.wiki',  required=False, type=str, help="Input extension of AMRs (default .sent)")
parser.add_argument("-output_ext", default = '.coref', required=False, type=str, help="Output extension of AMRs (default .tf)")
parser.add_argument("-python_path", default = '/home/p266548/Documents/amr_Rik/Seq2seq/src/python/', type=str, help="Path where we keep the Python source files")
args = parser.parse_args()

if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.input_ext):
				f_path = os.path.join(root, f)
				coref_call = 'python ' + args.python_path + 'place_coreferents.py -f {0}'.format(f_path)
				os.system(coref_call)
