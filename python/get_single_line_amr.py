import sys

def single_line_convert(f):
	single_amrs = []
	amr = []

	for line in open(f,'r'):
		if line[0] == '#':					
			continue
		elif not line.strip():
			single_line_amr = " ".join(amr)
			single_amrs.append(single_line_amr)
			amr = []
		else:									
			amr.append(line.strip())

	if amr:
		single_line_amr = " ".join(amr)
		single_amrs.append(single_line_amr)				# last one is not automatically added if there is no new line behind
	
	return single_amrs


if __name__ == "__main__":
	infile = sys.argv[1]
	out_file = sys.argv[2]
	
	single_amrs = single_line_convert(infile)
	single_amrs = [x for x in single_amrs if x]
	
	with open(out_file, 'w') as f:
		for line in single_amrs:
			f.write(line.strip() + '\n')
				
