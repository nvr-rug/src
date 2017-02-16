import os
import sys
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.sent',  required=False, type=str, help="Input extension (default .sent))")

args = parser.parse_args()

if __name__ == '__main__':
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.input_ext) and 'char' not in f:
				f_path = os.path.join(root, f)	
				os_call = "cat {0} | sed -e 's/|/\//g' | sed 's/^ *//;s/ *$//;s/  */ /g;' | /net/gsb/pmb/ext/candc/bin/pos --model /net/gsb/pmb/ext/candc/models/boxer/pos/ --output {1} --maxwords 5000".format(f_path, f_path + '.pos_temp')
				os.system(os_call)
				#replace POS-tags for punctuation
				
				repl_call = "cat {0} | sed 's/,|,/,/g' | sed 's/\.|\./\./g' | sed 's/!|\./!/g' | sed 's/;|;/;/g' | sed 's/-|:/-/g' | sed 's/:|:/:/g' > {1}".format(f_path + '.pos_temp', f_path + '.pos')
				os.system(repl_call)
				os.system('rm {0}'.format(f_path + '.pos_temp'))
				
