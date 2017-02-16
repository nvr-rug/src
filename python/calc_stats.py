import os
import sys
import argparse
import re

'''Script that calculates statistics over the data'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with files with AMRs")
parser.add_argument("-amr_ext", default = '.txt', type=str, help="AMR extension")
args = parser.parse_args()


def remove_sense(string):
	 string = re.sub('~e\.[\d,]+','', string)
	 return string


def process_file(f):
	sent_words = []
	sent_char = []
	amr_char = []
	amr = ''
	easy = 0
	for line in open(f, 'r'):
		if not line.strip():
			amr_char_len = len(amr.replace(' ',''))
			amr_char.append(amr_char_len)
			amr = ''
		elif line.startswith('# ::tok'):
			char_len = len(line.strip().replace('# ::tok','').replace(' ',''))
			word_len = len(line.replace('# ::tok','').split())
			sent_words.append(word_len)
			sent_char.append(char_len)
			if word_len < 6:
				easy += 1
		elif not line.startswith('# ::') and line.strip():
			amr += remove_sense(line).strip()
		
	if amr:
		amr_char_len = len(amr.replace(' ',''))
		amr_char.append(amr_char_len)				
	
	amr_char = amr_char[1:]
	assert (len(sent_words) == len(sent_char) == len(amr_char))
	
	avg_sent_words = round(float(sum(sent_words)) / float(len(sent_words)),1)
	avg_sent_char = round(float(sum(sent_char)) / float(len(sent_char)),1)
	avg_amr_char = round(float(sum(amr_char)) / float(len(amr_char)),1)
	avg_easy = round(float(easy) / float(len(amr_char)) * 100,1)
	
	print f.split('-')[-1], avg_sent_words, avg_sent_char, avg_amr_char
	print easy, 'out of', len(amr_char),'meaning', avg_easy,'%\n'
				
	return sent_words, sent_char, amr_char, easy

if __name__ == '__main__':
	
	total_words = []
	total_char = []
	total_amr = []
	total_easy = 0
	
	for root, dirs, files in os.walk(args.f):
		for f in files:
			if f.endswith(args.amr_ext):
				f_path = os.path.join(root, f)
				sent_words, sent_char, amr_char, easy = process_file(f_path)
				total_words += sent_words
				total_char += sent_char
				total_amr += amr_char
				total_easy += easy
	
	avg_sent_words = round(float(sum(total_words)) / float(len(total_words)),1)
	avg_sent_char = round(float(sum(total_char)) / float(len(total_char)),1)
	avg_amr_char = round(float(sum(total_amr)) / float(len(total_amr)),1)
	avg_easy = round(float(easy) / float(len(total_amr)),1)
	
	print 'Average:', avg_sent_words, avg_sent_char, avg_amr_char, avg_easy			
