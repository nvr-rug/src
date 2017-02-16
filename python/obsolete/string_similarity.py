import sys
import random

train_f = sys.argv[1]
test_f = sys.argv[2]
	
	
def get_bigrams(string):
	'''
	Takes a string and returns a list of bigrams
	'''
	s = string.lower()
	return [s[i:i+2] for i in xrange(len(s) - 1)]


def string_similarity(str1, str2):
	'''
	Perform bigram comparison between two strings
	and return a percentage match in decimal form
	'''
	pairs1 = get_bigrams(str1)
	pairs2 = get_bigrams(str2)
	union  = len(pairs1) + len(pairs2)
	hit_count = 0
	for x in pairs1:
		for y in pairs2:
			if x == y:
				hit_count += 1
				break
	return (2.0 * hit_count) / union
	

if __name__ == "__main__":

	test_sen = [x.strip() for x in open(test_f,'r')]
	
	best_avg = 0
	idx = 0
	
	for line in open(train_f,'r'):
		sim = 0
		idx += 1
		if idx % 100 == 0:
			print idx
		
		random_test = random.sample(test_sen, 100)
		
		for t in random_test:
			sim += string_similarity(line, t)
		avg = float(sim) / float(len(test_sen))
		
		if avg > best_avg:
			best_avg = avg
			best_line = line
			best_idx = idx
			if idx > 2000:
				print 'new best line:',best_line

print 'Line {0} was the most similar with avg {1}'.format(best_idx, best_avg)
print best_line				
					

