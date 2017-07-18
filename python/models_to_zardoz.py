#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys,re,argparse, os
from time import gmtime, strftime

'''Script that sends models to Zardoz and then removes them from Peregrine - to save space'''

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="Directory with models")
parser.add_argument('-end', required = False, type = int, default = 25, help="Stop after we see this epoch")
args = parser.parse_args()


if __name__ == '__main__':
	stop = False
	
	while not stop:
		models = [f for f in os.listdir(args.f) if os.path.isfile(os.path.join(args.f + '/', f))]	#get all models
		
		if models:
			os.system("sleep 5")	#wait a bit until the model is fully saved, probably too much, but we have the time anyway
			for m in models: 
				if 'model' in m and 'epoch' in m: #extra check to ensure we do not accidentally delete other files
					model_ep  = int(re.search(r'epoch([\d]+)', m).group(1))	#errors when fails, extra check
					
					m_file = os.path.join(args.f, m)
					os_call = 'scp {0} p266548@zardoz.service.rug.nl:{0}'.format(m_file)
					os.system(os_call)	#move file
					os.system("sleep 5")
					os.system("rm {0}".format(m_file))
					
					t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
					print 'Moved model of epoch {0} at {1}'.format(model_ep, t)
					
					if model_ep >= args.end:
						print 'Model {0} is the last one, stop checking'.format(model_ep)
						stop = True
						break
		
		if not stop:
			os.system("sleep 300") #sleep for 5 minutes before checking again, no need to do this continiously				
