import sys
import os
import argparse
import amr
from amr import AMR

parser = argparse.ArgumentParser()
parser.add_argument("-f", required=True, type=str, help="to be processed file")
args = parser.parse_args()

def change_args(line,splitter):
	spl = line.split(splitter)
	arg_num = 50 * [0]
	index_args = 0
	line_parts = []
	
	for idx, item in enumerate(spl):
		#print index_args
		if idx > 0:		# skip first item of split
			add_number = arg_num[index_args]
			appender = str(add_number) + item[1:] 	#replace first number after ARG with appropriate number
			#print 'add number {0} for index_args {1}'.format(add_number, index_args)
			line_parts.append(appender)
			arg_num[index_args] += 1
			
			for num in range(len(arg_num)):				# if we are adding something we should reset count of all later ARGs
				if num > index_args:
					arg_num[num] = 0
			
		else:
			line_parts.append(item)	
		
		for ch in item:
			if ch == '(':
				index_args += 1
				#print index_args
			if ch == ')':
				index_args -= 1
				#print index_args
	
	return splitter.join(line_parts)			
					
def change_ops(line, splitter):
	line_parts = []
	par_split = line.split('(')		# check on parts when opening
	for item in par_split:
		if splitter in item:		# if we close then check for the splitter item
			#close_spl = item.split(')')
			#rest_line = ")".join(close_spl[1:])  # add rest of line already, only interested in between the parentheses ()
			between  = item.split(splitter)
			split_parts = []
			for idx, part in enumerate(between):
				if idx > 0:
					split_parts.append(str(idx) + part[1:])  # first character after splitter (:op) is changed to idx (automatic counting)
				else:
					split_parts.append(part)
			
			add_split = splitter.join(split_parts)
			line_parts.append(add_split)
						
		else:
			line_parts.append(item)	
	return "(".join(line_parts) # convert line parts back to line and return

if __name__ == "__main__":
	with open(args.f + '.psp','w') as of, open(args.f + '.psp.counts','w') as wf:
		for line in open(args.f,'r'):
			line = line.strip().replace('-00','-01')		## restore -00 sense to -01 sense
			of.write(line + '\n')							## write to first outfile
			line = change_args(line, 'ARG')						## change second ARG to ARG1, ARG2, etc, doesn't really work if NN doesn't properly learn parentheses
			line = change_ops(line,':op')						## change :op0 NAME1 :op0 NAME2 :op0 NAME3 to :op1 NAME1 :op2 NAME2 :op3 NAME3
			#print line	
			wf.write(line + '\n')								## write to second outfile
	
	#for idx, line in enumerate(open(args.f,'r')):
		#if idx < 5:
			#amr_parse = AMR.parse_AMR_line(line)
			#amr_parse.output_amr()
			#print '\n\n'
		##p = amr_parse.get_triples()
	##	for tp in p:
	##		for i in tp:
	##			print i
		##print '\n\n'	
		##amr_parse.output_amr()
