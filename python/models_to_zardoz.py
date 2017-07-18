#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Script that sends models to Zardoz and then removes them from Peregrine - to save space'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with models")
parser.add_argument('-e', required = False, type = int, default = 1, help="Only include folders starting from this epoch (default 1 = all)")
parser.add_argument("-epochs", required = False, type=int, nargs = '+', help="Only do these specific epochs (if not done already)")
parser.add_argument("-end", required = False, type=int, default = 25, help="If we encounter this epoch we process it, after which we stop")
args = parser.parse_args()



def argument_check():
	if args.e != 1 and args.epochs:
		print 'Dont do both a threshold and fixed number, exiting...'
		sys.exit(0)


if __name__ == '__main__':
	argument_check()
	stop = False
	
	while not stop:
		models = [f for f in os.listdir(args.f) if os.path.isfile(os.path.join(args.f + '/', f))]	#get all models
		
		for m in models:
			m_file = os.path.join(args.f, m)
			model_ep  = int(re.search(r'epoch([\d]+)', m).group(1))
			
			if args.epochs:
				if model_ep in args.epochs:
					print 'Keep ep {0}'.format(model_ep)
				else:
					print 'Delete ep {0}'.format(model_ep)	
			elif model_ep >= args.e:
				print 'Keep ep {0}'.format(model_ep)
			else:		
				print 'Delete ep {0}'.format(model_ep)
		
		os.system("sleep 10")	
					
