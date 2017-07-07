#!/usr/bin/env python
# -*- coding: utf8 -*-

'''Evaluate output of the symbolizer'''

import re,sys, argparse, os
reload(sys)

parser = argparse.ArgumentParser()
parser.add_argument("-p", required = True, type=str, help="Produced folders")
parser.add_argument("-g", required = True, type=str, help="Gold file target")
parser.add_argument("-gs", required = True, type=str, help="Gold file source")
parser.add_argument("-prod_ext", default = '.seq.sym', type=str, help="Gold file")
parser.add_argument("-exp_name", default = 'unnamed', type=str, help="Name of experiment")
parser.add_argument('-v', action='store_true', default=False, help="If true have verbose output")
parser.add_argument("-sig", required = False, default = 4, type=int, help="When do we stop rounding the accuracy")
args = parser.parse_args()


def get_accuracy(prod, gold, gold_src):
	'''Function that returns accuracy of the symbolizer'''
	
	if not len(gold) == len(prod) == len(gold_src):
		raise ValueError("Produced, gold and gold source file are of different length")
	
	cor, inc = 0,0
	
	for idx in range(len(prod)):
		if prod[idx] == gold[idx]:
			cor += 1
		else:
			inc += 1
			if args.v:
				print '{0} instead of {1}, for input: {2}'.format(prod[idx], gold[idx], gold_src[idx])
	if args.v:
		print '\n'
	acc = round(float(cor) / float(cor + inc), args.sig)
	
	return acc		


def print_results(res_list):
	if not res_list:
		print 'Something probably went wrong, results list is empty\n'
		sys.exit(0)
	
	sorted_res_list = sorted(res_list, key=lambda x: x[0])
	
	print 'Results for {0}:'.format(args.exp_name)
	print '\n          Accuracy'
	
	for r in sorted_res_list:
		if r[0] > 9:	#spacing issue in printing	
			print 'Epoch {0}: {1}'.format(r[0], r[1])
		else:
			print 'Epoch {0} : {1}'.format(r[0], r[1])	


if __name__ == '__main__':
	gold = [x.strip() for x in open(args.g,'r')]
	gold_src = [x.strip() for x in open(args.gs,'r')]
	res_list = []
	
	for root, dirs, files in os.walk(args.p):
		for f in files:
			if f.endswith(args.prod_ext):
				f_path = os.path.join(root, f)
				if os.path.getsize(f_path) > 0:	#check if file has content
					epoch  = int(re.findall(r'epoch([\d]+)', f_path)[0])				#get epoch number
					prod   = [x.replace(' ','').strip() for x in open(f_path,'r')]
					acc    = get_accuracy(prod, gold, gold_src)	
					res_list.append([epoch, acc])
	
	print_results(res_list)				
