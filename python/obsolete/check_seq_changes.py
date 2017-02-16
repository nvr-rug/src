import sys
import re
import subprocess
import os

'''Script that produces the Smatch output for produced seq2seq parses,
   which shows how similar the outputs are'''

# python check_seq_changes.py output/1lay_400s_24k/test/ output/1lay_400s_50k/test/ output/1lay_400s_111k/test/ output/1lay_400s_150k/test/ output/1lay_400s_205k/test/

# input: all folders that need to be checked (specify dev/test)

folders = sys.argv

# mooie forloops zijn niet lelijk

for idx in range(len(folders)):
	for idx2 in range(idx+1, len(folders)):
		for root, dirs, files in os.walk(folders[idx]):
			f_scores = []
			total_f = 0
			total_sen = 0
			for f in files:
				if f.endswith('.psp'):
					#print 'file:',f
					for root2,dirs2, files2 in os.walk(folders[idx2]):
						for f2 in files2:
							if f == f2:
								file_path1 = os.path.join(root, f)
								file_path2 = os.path.join(root2, f2)
								num_sen = sum(1 for line in open(file_path1))
								smatch_call = 'python ../Boxer/smatch_2.0.2/smatch.py -r 4 --both_one_line -f {0} {1}'.format(file_path1, file_path2)
								output = subprocess.check_output(smatch_call, shell=True)
								f_score = float(output.split()[-1])
								f_scores.append(f_score)
								total_f += num_sen * f_score
								total_sen += num_sen

			#print f_scores
			print 'Similarity:',folders[idx].split('_')[-1],'en',folders[idx2].split('_')[-1], f_scores
			print 'Average similarity: {0}'.format(float(total_f) / float(total_sen))
