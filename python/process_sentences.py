#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Script that tokenizes and possibly lemmatizes the sentences. For lemmatizing we also need to POS-tags
   Set the -amr variable if it should be done on separate sentences (not allowing Elephant to create new ones)'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with sentence files")
parser.add_argument("-sent_ext", default = '.sent',  required=False, type=str, help="Extension of sentence file")
parser.add_argument("-tok_ext", default = '.tok',  required=False, type=str, help="Extension of tok file")
parser.add_argument("-pos_ext", default = '.pos',  required=False, type=str, help="Extension of POS file")
parser.add_argument("-lemma_ext", default = '.lemma',  required=False, type=str, help="Extension of lemma file")
parser.add_argument('-amr', action='store_true', help='Process sentences per line, as for AMRs')
parser.add_argument('-lem', action='store_true', help='Do lemmatization')
args = parser.parse_args()


def write_to_file(lst, f):
	with open(f, 'w') as out:
		for l in lst:
			out.write(l.strip() + '\n')
	out.close()


def tokenize_amr(f, out_f):
	'''Put sentences in word-level input
	   If errors: run this: export PATH=/net/gsb/gsb/ext/elephant:/net/gsb/gsb/ext/elephant/ext:$PATH
	   Do this on sentence level for AMRs, because Elephant also creates new sentences, which is obviously not wanted'''
	sents = []
	os.system("export PATH=/net/gsb/gsb/ext/elephant:/net/gsb/gsb/ext/elephant/ext:$PATH")
	print 'Start tokenizing', f
	
	for idx, s in enumerate(open(f, 'r')):
		
		if idx % 200 == 0:
			print idx
		
		with open('temp.toktmp','w') as tmp:
			tmp.write(s.strip())
		tmp.close()	
		
		os.system("cat temp.toktmp | /net/gsb/gsb/ext/elephant/elephant -m /net/gsb/gsb/ext/elephant/models/english/ -f iob | sed -e 's/\t/ /'  > temp.tok.iob".format(s))
		os.system("cat temp.tok.iob | ~/Documents/pmb_lc/src/python/iob2off.py > temp.tok.off")
		os.system("cat temp.tok.off | /net/gsb/pmb/src/python/off2tok.py > temp.tok")
		
		new_sent = " ".join([x.strip() for x in open('temp.tok','r')])
		sents.append(new_sent)

		os.system("rm temp.tok*".format(f))	#remove temp files
	
	write_to_file(sents, out_f)	


def tokenize(f, out_f):
	'''Do tokenization for set of sentences'''
	
	os.system("export PATH=/net/gsb/gsb/ext/elephant:/net/gsb/gsb/ext/elephant/ext:$PATH")
	os.system("cat {0} | /net/gsb/gsb/ext/elephant/elephant -m /net/gsb/gsb/ext/elephant/models/english/ -f iob | sed -e 's/\t/ /'  > temp.tok.iob".format(f))
	os.system("cat temp.tok.iob | ~/Documents/pmb_lc/src/python/iob2off.py > temp.tok.off")
	os.system("cat temp.tok.off | /net/gsb/pmb/src/python/off2tok.py > {0}".format(out_f))
	os.system("rm temp.tok*".format(f))	#remove temp files


def pos_tag(f, out_f):
	os.system('''cat {0} | sed -e "s/[‘’]/'/g" | sed -e 's/[“”]/"/g' | sed -e 's/|/\//g' | /net/gsb/pmb/ext/candc/bin/pos --maxwords 1000 --model /net/gsb/pmb/ext/candc/models/boxer/pos > {1}'''.format(f, out_f))


def lemmatize(f, out_f):
	new_lines = []

	
	for line in open(f, 'r'):
		#print line
		with open('lem.temp.wr','w') as tmp:
			tmp.write(line.strip())
		tmp.close()
		os.system('''cat lem.temp.wr | /net/gsb/pmb/src/python/pos2morpha.py | /net/gsb/pmb/ext/morph/morpha -f /net/gsb/pmb/ext/morph/verbstem.list > lem.temp''')
		#os.system('''/home/p266548/Documents/test/morpha2lemma.py {0} lem.temp | /net/gsb/pmb/src/python/lemma2cols.py > lem.temp.out'''.format(f, out_f))
		
		new_line = " ".join([x.strip().lower() for x in open('lem.temp','r')])
		new_lines.append(new_line)
		
		os.system("rm lem.temp*")
	
	write_to_file(new_lines, out_f)


if __name__ == "__main__":
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.sent_ext) and 'char' not in f:		#always do tokenization
				f_path = os.path.join(root, f)
				tok_out = f_path + args.tok_ext
				if args.amr:
					tokenize_amr(f_path, tok_out)
				else:
					tokenize(f_path, tok_out)
				
				if args.lem:	#also do lemmatization		
					pos_out = f_path + args.pos_ext
					lem_out = f_path + args.lemma_ext
					
					pos_tag(tok_out, pos_out)
					lemmatize(pos_out, lem_out)
