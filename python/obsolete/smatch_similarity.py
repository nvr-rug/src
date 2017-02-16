import sys
import random
import subprocess
import time

'''Script that compares all AMRs in train set with the AMRs in test/dev set. 
   First we compare each train instance with 100 randomly chosen dev/test instances,
   the best 200 instances are then compared to ALL dev/test instances to find the 
   best one (otherwise it takes way too long)'''


train_f = sys.argv[1]
test_f = sys.argv[2]
	
if __name__ == "__main__":

	test_sen = [x.strip() for x in open(test_f,'r')]
	train_sen = [x.strip() for x in open(train_f,'r')]
	idx = 0	
	best_fscore = 0
	best_list = [[0.05,'ok',1]]
	random_num = len(test_sen)
	
	for line in train_sen:
		if idx % 100 == 0:
			print idx
		#print line
		random_test = random.sample(test_sen, random_num)
		
		with open('temp1.txt','w') as temp1:
			l = line.strip() + '\n'
			temp1.write(l * random_num)
		temp1.close()	
		
		with open('temp2.txt','w') as temp2:
			for line in random_test:
				temp2.write(line.strip() + '\n')
		temp2.close()		
		
		os_call = 'python ./Boxer/smatch_2.0.2/smatch.py -r 1 --both_one_line -f {0} {1}'.format('temp1.txt', 'temp2.txt')
		output = subprocess.check_output(os_call, shell=True)
		f_score = float(output.split()[-1])
		
		if f_score > 0.2:
			print f_score
			print line
		
		#if f_score > best_list[-1][0]:
			#best_list.append([f_score, line, idx])
			#best_list.sort(key=lambda x: x[0], reverse = True)
			##print best_list[:5]
			#if len(best_list) > 200:
				#best_list = best_list[:200]
		
		idx += 1		
	
	## test best 200 instances again, but now on all dev instances to really make sure
	
	#new_best_list = []
	#for lst in best_list:
		#idx = lst[2]
		#line = train_sen[idx]
		
		#with open('temp1.txt','w') as temp1:
			#l = line.strip() + '\n'
			#temp1.write(l * len(test_sen))
		#temp1.close()	
		
		#with open('temp2.txt','w') as temp2:
			#for line in test_sen:
				#temp2.write(line.strip() + '\n')
		#temp2.close()
		
		#os_call = 'python ./Boxer/smatch_2.0.2/smatch.py -r 1 --both_one_line -f {0} {1}'.format('temp1.txt', 'temp2.txt')
		#output = subprocess.check_output(os_call, shell=True)
		#f_score = float(output.split()[-1])				
		#print f_score
		#new_best_list.append([f_score, line, idx])
	
	#new_best_list.sort(key=lambda x: x[0], reverse = True)	
	
	#with open('most_common_amr.txt','w') as out_f:
		#for count, item in enumerate(new_best_list):
			#out_f.write(str(count)+ ':', str(item[2]), str(item[0]), item[1] +'\n')				
					

