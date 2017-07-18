#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os

'''Script that sends models to Zardoz and then removes them from Peregrine - to save space'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with models")
args = parser.parse_args()


if __name__ == '__main__':
	stop = False
	
	while not stop:
		models = [f for f in os.listdir(args.f) if os.path.isfile(os.path.join(args.f + '/', f))]	#get all models
		
		if models:
			os.system("sleep 5")	#wait a bit until the model is fully saved
			for m in models:
				if 'model' in m: #extra check to ensure we do not accidentally delete other files
					m_file = os.path.join(args.f, m)
					os_call = 'python ~/hulp_scripts/zardoz_sender.py {0}'.format(m_file)
					print os_call
					
