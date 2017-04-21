import sys
import re
import argparse
import os
import subprocess
import validator_seq2seq
import wikification_seq2seq
from multiprocessing import Pool
from datetime import datetime

'''Script that checks if produced JAMR/CAMR AMRs are valid'''

parser = argparse.ArgumentParser()
parser.add_argument('-c', required = True,help="CAMR output files")
parser.add_argument('-j', required = True,help="JAMR output files")
parser.add_argument('-vc', required = True,help="Validated CAMR output files")
parser.add_argument('-vj', required = True,help="Validated JAMR output files")
parser.add_argument('-camr_ext', default = '.camr.amr',help="CAMR output ext")
parser.add_argument('-jamr_ext', default = '.jamr.amr',help="JAMR output ext")
args = parser.parse_args() 


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
	out_f.close()

def write_to_file_extra_newline(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n\n')
	out_f.close()	


def get_paired_dict(d, ext_d, file_dict):
	for root, dirs, files in os.walk(d):
		for f in files:
			if f.endswith(ext_d):
				raw_f = f.replace(ext_d,'')
				if raw_f not in file_dict:
					file_dict[raw_f] = [os.path.join(root,f)]
				else:
					file_dict[raw_f].append(os.path.join(root,f))	
	
	return file_dict				


def get_one_line_amrs(f):
	all_amrs = []
	cur_amr = []
	sents = []
	for line in f:
		if not line.strip():
			cur_amr_line = " ".join(cur_amr)
			all_amrs.append(cur_amr_line.strip())
			cur_amr = []
		elif line.startswith('# ::'):
			if line.startswith('# ::snt'):
				if '[Text=' in line:			#something went wrong in JAMR, remove this	
					to_add = line.split('[Text=')[0].replace('# ::snt','').strip()
					sents.append(to_add)
				else:
					sents.append(line.replace('# ::snt','').strip())
		else:	
			cur_amr.append(line.strip())	
				
	return all_amrs, sents		


def check_valid(camr, jamr, camr_sents):
	new_camr = []
	new_jamr = []
	new_sents = []
	
	inv_camr, inv_jamr, valid = 0, 0, 0
	
	for idx in range(len(camr)):
		if not validator_seq2seq.valid_amr(camr[idx]):
			inv_camr += 1
		elif not validator_seq2seq.valid_amr(jamr[idx]):	
			inv_jamr += 1
		else:
			valid += 1
			new_camr.append(camr[idx])
			new_jamr.append(jamr[idx])
			new_sents.append(camr_sents[idx])
		
	return new_camr, new_jamr, new_sents, inv_camr, inv_jamr, valid		


def get_amr_tree(amrs, sents):
	fixed_amrs = []
	prev_ch = ''
	for idx, line in enumerate(amrs):
		num_tabs = 0
		amr_string = '# ::snt ' + sents[idx] + '\n'
		for ch in line:
			if ch == '(':
				num_tabs += 1
				amr_string += ch
			elif ch == ')':
				num_tabs -= 1
				amr_string += ch
			elif ch	 == ':':	
				if prev_ch == ' ':	#only do when prev char is a space, else it was probably a HTML link or something
					amr_string += '\n' + num_tabs * '\t' + ch
				else:
					amr_string += ch	
			else:
				amr_string += ch
			prev_ch = ch
				
		amr_string += '\n'
		fixed_amrs.append(amr_string)
	
	return fixed_amrs			
			
if __name__ == "__main__":
	file_dict = {}
	file_dict = get_paired_dict(args.c, args.camr_ext, file_dict)
	file_dict = get_paired_dict(args.j, args.jamr_ext, file_dict)
	
	print len(file_dict)
	
	total_inv_camr, total_inv_jamr, total_valid, file_count = 0, 0, 0, 0
	
	for key in file_dict:
		if len(file_dict[key]) == 2:
			file_count += 1
			
			if file_count % 50 == 0:
				print 'File count: {3}\nInvalid CAMR: {0}\nInvalid JAMR: {1}\nValid AMRs: {2}\n'.format(total_inv_camr, total_inv_jamr, total_valid, file_count)
			
			camr_ml = [x.strip() for x in open(file_dict[key][0],'r')]
			jamr_ml = [x.strip() for x in open(file_dict[key][1],'r')]
			
			camr, camr_sents = get_one_line_amrs(camr_ml)
			jamr, jamr_sents = get_one_line_amrs(jamr_ml)
			
			if len(jamr) == len(camr) == len(camr_sents):
				new_camr, new_jamr, new_sents, inv_camr, inv_jamr, valid = check_valid(camr, jamr, camr_sents)	
				camr_tree = get_amr_tree(new_camr, new_sents)
				jamr_tree = get_amr_tree(new_jamr, new_sents)
				
				out_camr = args.vc + file_dict[key][0].split('/')[-1]
				out_jamr = args.vj + file_dict[key][1].split('/')[-1]
				out_camr_ol = args.vc + file_dict[key][0].split('/')[-1] + '.ol'
				out_jamr_ol = args.vj + file_dict[key][1].split('/')[-1] + '.ol'
				out_camr_sents = args.vc + file_dict[key][0].split('/')[-1] + '.sent'
				out_jamr_sents = args.vj + file_dict[key][1].split('/')[-1] + '.sent'
				
				write_to_file_extra_newline(camr_tree, out_camr)
				write_to_file_extra_newline(jamr_tree, out_jamr)
				write_to_file(new_camr, out_camr_ol)
				write_to_file(new_jamr, out_jamr_ol)
				write_to_file(new_sents, out_camr_sents)
				write_to_file(new_sents, out_jamr_sents)
				
				total_inv_camr += inv_camr
				total_inv_jamr += inv_jamr
				total_valid += valid
			else:
				print 'Skip these files, wrong length, {0} vs {1}'.format(len(camr), len(jamr))
	
	print 'Invalid CAMR: {0}\nInvalid JAMR: {1}\nTotal valid: {2}\n'.format(total_inv_camr, total_inv_jamr, total_valid)			
			
	
