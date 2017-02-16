import sys

def single_line_convert(f):
	single_amrs = []
	prev_amr = False
	for line in open(f,'r'):
		if line[0] != '#':					# skip non-amr lines
			if prev_amr:
				amr.append(line.strip())
			else:
				amr = [line.strip()]
			prev_amr = True
		else:									# start a new AMR to convert
			if prev_amr:
				single_line_amr = " ".join(amr)
				single_amrs.append(single_line_amr)
				#print single_line_amr
			prev_amr = False

	if amr != [] and amr != '':
		single_line_amr = " ".join(amr)
		single_amrs.append(single_line_amr)				# last one is not automatically added due to missing '#'
	
	return single_amrs


if __name__ == "__main__":
	infile = sys.argv[1]
	out_file = sys.argv[2]
	
	single_amrs = single_line_convert(infile)
	single_amrs = [x for x in single_amrs if x]
	
	with open(out_file, 'w') as f:
		for line in single_amrs:
			f.write(line.strip() + '\n')
				
