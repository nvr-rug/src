import sys, os

'''Script that fixes all weird unicode'''

root_folder = sys.argv[1]
out_root = sys.argv[2]

for root, dirs, files in os.walk(root_folder):
	for f in files:
		fix_l = []
		file_path = os.path.join(root, f)
		
		for l in open(file_path,'r'):
			fix_l.append(l.replace('\xc2\x91','\'').replace('\xc2\x92','\'').replace('\xc2\x93','"').replace('\xc2\x94','"').replace('\xc2\x85','...').replace('\xc2\x97','-').replace('\xc2\x96','-').replace('\xc2\x99','').replace('\xc2\x95',''))
		out_file = out_root + file_path.split('amrs/')[1]
		print out_file
		
		with open(out_file,'w') as f:	# print fixed AMRs and sentences to same file in new folder (data_2017_fixed_unicode)
			for l in fix_l:
				f.write(l)

