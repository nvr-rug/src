import os
import sys
import argparse
import time

'''Script that represents some words as chunks instead of characters in for the model-input
   E.g. c o u n t r y becomes country'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="directory that contains amrs / sentences to be processed")
parser.add_argument("-input_ext", default = '.char.tf',  required=False, type=str, help="Input extension of AMRs (default .char.tf)")
parser.add_argument("-chunks", default = '/home/p266548/Documents/amr_Rik/dicts/list_of_chunks.txt', type=str, help="File with all words that are represented as chunks instead of characters")

args = parser.parse_args()

def get_chunk_reps(chunked_words):
	new_chunk_reps = []
	
	for chunk in chunked_words:
		new_word = ''
		for ch in chunk:
			new_word += ch + ' '
		new_chunk_reps.append(new_word.strip())
	
	assert len(new_chunk_reps) == len(chunked_words)
	
	return new_chunk_reps			

if __name__ == '__main__':
	start = time.time()
	chunked_words = [x.strip() for x in open(args.chunks,'r')]		#import words that we want to keep as chunks
	chunk_reps = get_chunk_reps(chunked_words)						#get the representations of those chunks at character-level
	
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.input_ext):
				f_path = os.path.join(root, f)
				new_lines = []
				for line in open(f_path, 'r'):
					for match, repl in zip(chunk_reps, chunked_words):
						if match in line:
							line = line.replace(match, repl)		#replace the matched chunk with the word that is not on character-level				
					new_lines.append(line)
				
				with open(f_path, 'w') as out_f:
					for l in new_lines:
						out_f.write(l.strip() + '\n')
				out_f.close()			
