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
parser.add_argument('-camr_ext', default = '.camr.amr.ol',help="CAMR output ext")
parser.add_argument('-jamr_ext', default = '.jamr.amr.ol',help="JAMR output ext")
args = parser.parse_args() 


def write_to_file(lst, f):
	with open(f,'w') as out_f:
		for l in lst:
			out_f.write(l.strip() + '\n')
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
	for line in open(args.f,'r'):
		if not line.strip():
			cur_amr_line = " ".join(cur_amr)
			all_amrs.append(cur_amr_line.strip())
			cur_amr = []
		elif not line.startswith('# ::'):
			cur_amr.append(line.strip())
	
	return all_amrs		


def check_valid(camr, jamr):
	new_camr = []
	new_jamr = []
	
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
		
	return new_camr, new_jamr, inv_camr, inv_jamr, valid		
			
			
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
			
			camr = [x.strip() for x in open(file_dict[key][0],'r')]
			jamr = [x.strip() for x in open(file_dict[key][1],'r')]
			if len(jamr) != len(camr):
				print 'Skip these file, wrong length, {0} vs {1}'.format(len(camr), len(jamr))
			else:
				new_camr, new_jamr, inv_camr, inv_jamr, valid = check_valid(camr, jamr)	
				out_camr = args.vc + file_dict[key][0].split('/')[-1]
				out_jamr = args.vj + file_dict[key][1].split('/')[-1]
				
				write_to_file(new_camr, out_camr)
				write_to_file(new_jamr, out_jamr)
				
				total_inv_camr += inv_camr
				total_inv_jamr += inv_jamr
				total_valid += valid
	
