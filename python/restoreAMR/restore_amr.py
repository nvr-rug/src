#!/usr/bin/env python3

import sys, re, os, json, random
from trans import translate, restore
import validator_seq2seq

#def usage():
 #   print('usage:', sys.argv[0], '[--plain] [--apply-on <comment tag>] < input.amr > output.amr', file=sys.stderr)

args = sys.argv[1:]

unbracket = re.compile(r'\(\s*([^():\s"]*)\s*\)')
dangling_edges = re.compile(r':[\w\-]+\s*(?=[:)])')
missing_edges = re.compile(r'(\/\s*[\w\-]+)\s+\(')
missing_variable = re.compile(r'(?<=\()\s*([\w\-]+)\s+(?=:)')
missing_quotes = re.compile(r'("\w+)(?=\s\))')
misplaced_colon = re.compile(r':(?=\))')
missing_concept_and_variable = re.compile(r'(?<=\()\s*(?=:\w+)')
dangling_quotes = re.compile(r'(?<=\s)(\w+)"(?=\s|\)|:)')

# c = 0
def replace_var(m):
	global c
	global cc
	global ggg
#    counter += 1
	# line = re.sub(r'\(\s*([\w\-\d]+)(\W)', replace_var, line)
	if ['name','date'].count(m.group(1)) == 1:
		c += 1
		return '(v' + str(ggg) + str(c) + ' / ' + m.group(1) + m.group(2)
	if cc.count(m.group(1)) == 0:
		cc.append(m.group(1))
		return '(vv' + str(ggg) + m.group(1) + ' / ' + m.group(1) + m.group(2)
	if m.group(2) == ' )':
	   return ' vv' + str(ggg) + m.group(1)
	c += 1
	return '(vvvv' + str(ggg) + str(c) + ' / ' + m.group(1) + m.group(2)
	

def replace_var2(m):
#    global counter
	if m.group(2) == "-":
		return "%s %s" % (m.group(1), m.group(2))
	if m.group(2) == "interrogative":
		return "%s %s" % (m.group(1), m.group(2))
	if m.group(2) == "expressive":
		return "%s %s" % (m.group(1), m.group(2))
	if m.group(2) == "imperative":
		return "%s %s" % (m.group(1), m.group(2))
#    counter += 1
	return "%s \"%s\"" % (m.group(1),  m.group(2))


def add_quotes(m):
	value = m.group(2).strip()
	if value == '-':
		return '%s %s ' % (m.group(1), value)
	return '%s "%s" ' % (m.group(1), value)

def convert(line):
	global cc
	global c
	global ggg
	c = 0
	cc=[]
	old_line = line
	while True:
		line = re.sub(r'(\( ?name [^()]*:op\d+|:wiki) ([^\-_():"][^():"]*)(?=[:\)])', add_quotes, line, re.I)
		# line = re.sub(r'((:op\d+|:wiki) ([^():"]+)(?=[:\)])', add_quotes, line, re.I)
		if old_line == line:
			break
		old_line = line

	line = re.sub(r'\(\s*([\w\-\d]+)(\W.|\))', replace_var, line)

	# print('>>', line)
	# line = re.sub(r'(?<=\s)(_\w+)(?=[\s)]|$)', lambda m: restore(m.group(1)), line)
	# re.sub(r'(?<=\s)(_\w+)(?=[\s)]|$)', lambda m: print(m.group(1)), line)
	line = re.sub(r'"(_[^"]+)"', lambda m: restore(m.group(1)), line)
	# line = re.sub(r'(?<=\s)(_\w+)(?=[\s)]|$)', lambda m: restore(m.group(1)), line)

	open_count = 0
	close_count = 0
	for i,c in enumerate(line):
		if c == '(':
			open_count += 1
		elif c == ')':
			close_count += 1
		if open_count == close_count and open_count > 0:
			line = line[:i].strip()
			break

	old_line = line
	while True:
		open_count = len(re.findall(r'\(', line))
		close_count = len(re.findall(r'\)', line))
		if open_count > close_count:
			line += ')' * (open_count-close_count)
		elif close_count > open_count:
			before = line
			for i in range(close_count-open_count):
				line = line.rstrip(')')
				line = line.rstrip(' ')
		#     if before == line:
		#         line = '(' * (close_count-open_count) + line
		if old_line == line:
			break
		old_line = line

	old_line = line
	while True:
		line = re.sub(r'(:\w+) ([^\W\d\-][\w\-]*)(?=\W)', replace_var2, line, re.I)
		if old_line == line:
			break
		old_line = line
	line = unbracket.sub(r'\1', line, re.U)

	line = dangling_edges.sub('', line, re.U)

	line = missing_edges.sub(r'\1 :ARG2 (', line, re.U)

	line = missing_variable.sub(r'vvvx / \1 ', line, re.U)

	line = missing_quotes.sub(r'\1"', line, re.U)

	line = misplaced_colon.sub(r'', line, re.U)

	line = missing_concept_and_variable.sub(r'd / dummy ', line, re.U)

	line = dangling_quotes.sub(r'\1', line, re.U)

	return line

def add_space_when_digit(line, id_list):
	spl = line.split(':')
	for idx in range(1, len(spl)):
		if spl[idx].strip().replace(')',''):
			if (spl[idx].strip().replace(')','')[-1].isdigit() and (not any(x in spl[idx] for x in id_list))):        ## if there is a digit after quant or value, put a space so we don't error, e.g. :value3 becomes :value 3, but not for op, snt and ARG
				new_string = ''
				added_space = False
				for ch in spl[idx]:
					if ch.isdigit():
						if not added_space:
							new_string += ' ' + ch
							added_space = True
						else:
							new_string += ch    
					else:
						new_string += ch
				spl[idx] = new_string
			
			elif (spl[idx].replace(')','').replace('ARG','').isdigit()):                #change ARG2444 to ARG2 444
				spl[idx] = re.sub(r'(ARG\d)([\d]+)',r'\1 \2',spl[idx])
	return ':'.join(spl)      
		

def do_extra_steps(line):
	line = line.replace(':',' :')               # dubbele punt has no spaces
	line = line.replace('(',' (')
	for x in range(0,25):                       # change :op0"value" to :op0 "value" as to avoid errors
		line = line.replace(':op' + str(x) + '"', ':op' + str(x) + ' "')
	
	line = line.replace(':value"',':value "')
	line = line.replace(':time"',':time "')
	line = line.replace(':li"',':li "')
	line = line.replace(':mod"',':mod "')
	line = line.replace(':timezone"',':timezone "')
	line = line.replace(':era"',':era "')
	
	quotes = 0
	prev_char = 'a'
	new_line = ''
	
	for ch in line:
		if ch == '"':
			quotes += 1
			if quotes % 2 != 0 and new_line[-1] != ' ':
				new_line += ' "'                            #add space for quote
			else:
				new_line += ch  
		else:
			new_line += ch
	
	new_line = re.sub('(op\d)(\d\d+)',r'\1 \2',new_line)     #fix problem with op and numbers, e.g. change op123.5 to op1 23.5           
	new_line = re.sub(r'(op\d)(\d+)\.(\d+)',r'\1 \2.\3',new_line)
	new_line = re.sub(r'(mod\d)(\d+)\.(\d+)',r'\1 \2.\3',new_line)
	new_line = re.sub(r'(ARG\d)(\d+)\.(\d+)',r'\1 \2.\3',new_line)
	new_line = new_line.replace(':polarity 100',':polarity -')
	return new_line


#def undo_brackets(line, replace_char):
	#new_line = '(' + line.strip() + ')'							#restore opening and closing brackets
	#if replace_char:
		#new_line = re.sub(r'\*\d(\d+)?\(\*',r'(',new_line)		#change *1)* to ) or *5(* to (
		#new_line = re.sub(r'\*\d(\d+)?\)\*',r')',new_line)
	#else:
		#new_line = re.sub(r'\*\d(\d+)?\(\*','',new_line)		#remove *1)* and *5(*
		#new_line = re.sub(r'\*\d(\d+)?\)\*','',new_line)	
	#return new_line


def get_most_frequent_referent(seen_coref, ref_dict):
	most_freq = ''
	score = -1
	
	for item in seen_coref:					
		if seen_coref[item] in ref_dict:				#if this word in general dict
			if ref_dict[seen_coref[item]] > score:		#check if it is the most frequent
				score = ref_dict[seen_coref[item]]
				most_freq = seen_coref[item]
	
	if score > -1:
		#print 'Variable not instantiated, return most frequent referent: {0}'.format(most_freq)
		return most_freq							#return most frequent referent we saw
	else:	
		rand_key = random.choice(seen_coref.keys())		#if no referents with score, return a random one
		#print 'Variable not instantiated, return random referent: {0}'.format(most_freq)
		return seen_coref[rand_key]


def get_most_frequent_word(tok_line, ref_dict):
	most_freq = ''
	score = -1
	words = []
	
	for item in tok_line:
		if item[0].isalpha():
			words.append(item)
			if item in ref_dict:
				if ref_dict[item] > score:
					score = ref_dict[item]
					most_freq = item
	
	if score > -1:			
		return most_freq		#return word that most often has a referent in training set
	elif words:		
		rand_return = random.choice(words[0:-1]) if len(words) > 1 else random.choice(words)
		return rand_return		#no known words from our training set, return random one, last one might be cut-off though so ignore that one
	else:
		return 'person'	
				
def restore_coref(line, ref_dict):
	'''Restore coreference items, e.g. *3* and *2* with actual word'''
	
	pattern = re.compile('^\*[\d]+\*$')
	
	tok_line = line.replace(')',' ) ').replace('(',' ( ').split()	# "tokenize" line
	seen_coref = {}
	new_tok = []
	
	ref = get_most_frequent_word(tok_line, ref_dict)
	
	for idx, item in enumerate(tok_line):
		if pattern.match(item):
			if idx < len(tok_line) -1 and tok_line[idx+1][0].isalpha():			#check if next is a word
				seen_coref[item] = tok_line[idx+1]		#always add if it's a word
	
	
	for idx, item in enumerate(tok_line):
		if pattern.match(item):	
			if idx == len(tok_line) -1:		#can't look ahead to idx + 1 here
				referent = get_most_frequent_word(tok_line, ref_dict)
				new_tok.append('(coref-{0})'.format(referent))
			elif tok_line[idx+1][0].isalpha():		#just remove coref instance, word is there, so do not add anything
				pass
			else:									#replace coref instance	
				if item in seen_coref:
					referent = seen_coref[item]
					#print 'Normal coreference'
				else:								#referent in output, but was never added - what now?
					#if len(seen_coref) > 0:			#current solution, add most frequent other referent, if they are all not in train set add one at random
					#	print 'There are other referents'
					#	referent = get_most_frequent_referent(seen_coref, ref_dict)
					#else:							#if there are no other referents just add the most frequent one in general based on all words in sentence
					referent = get_most_frequent_word(tok_line, ref_dict)	#get word that is most frequently referred to
					#print 'Coference based on most frequent word'
					
				new_tok.append('(coref-{0})'.format(referent))	#bit hacky/ugly, but we have no variables here, we need to recognize that we need to replace this word in a later stage without messing up the restoring variables process		
																#we also add unneccesary brackets to not mess up the variable restoring process, we need to remove them in a later stage as well	
		else:
			new_tok.append(item)
	
	new_line = " ".join(new_tok)
	
	while ' )' in new_line or '( ' in new_line:								#reverse the tokenization process
		new_line = new_line.replace(' )',')').replace('( ','(')

					
	return new_line


def add_coref(line):		#this line includes variables, but we still need to replace 'COREF-person' with 'p', for example
	var_dict = {}			#first get the variables
	tok_line = line.replace(')',' ) ').replace('(',' ( ').split()						
	#print line
	for idx, item in enumerate(tok_line):
		if item == '/':			#variable in previous tok and value in tok afterwards
			if 'coref-' not in tok_line[idx+1]:
				var_dict[tok_line[idx+1]] = tok_line[idx-1]	
	
	new_tok = []
	
	ignore_next = False
	
	for idx, item in enumerate(tok_line):		#add coref back
		if item.startswith('coref-'):
			ignore_next = False
			it = item.replace('coref-','')
			if it in var_dict:
				#print 'Replace {0} with {1}'.format(item, var_dict[it])
				new_tok.append(var_dict[it])
				#remove previous 3 items, " ( var / " and next item " ) "
				new_tok[-2] = ''
				new_tok[-3] = ''
				new_tok[-4] = ''
				ignore_next = True
			else:
				#print '{0} is unknown, should never happen, just add person now'.format(it)
				new_tok.append('person')
				new_tok[-2] = ''
				new_tok[-3] = ''
				new_tok[-4] = ''
				ignore_next = True	
		elif not ignore_next:
			new_tok.append(item)
			ignore_next = False	
		else:
			ignore_next = False
	
	new_line = " ".join(new_tok)
	
	while ' )' in new_line or '( ' in new_line:								#reverse the tokenization process
		new_line = new_line.replace(' )',')').replace('( ','(')
					
	return new_line

global ggg
ggg = 0

lines = [x.strip() for x in open(sys.argv[1], 'r')]
lines_as_str = " ".join(lines)

coref_inst = len(re.findall(r'\*[\d]+\*', lines_as_str))	#find all coreference instances

if coref_inst > 20: #check whether we have to fix coref characters first
	coref = True
	
	with open('/home/p266548/Documents/amr_Rik/Seq2seq/src/python/restoreAMR/ref_dict', 'r') as in_f:				#load reference dict (based on training data) to settle disputes based on frequency
		ref_dict = json.load(in_f)
	in_f.close()
	
	#print 'Doing coreference in restore script, {0} instances'.format(coref_inst)
else:
	#print 'Not doing coreference in restore script'
	coref = False	


for idx, line in enumerate(lines):
	#print idx + 1
	ggg += 1
	
	line = line.replace(' ','').replace('+',' ').replace(':polarity-',':polarity100')	
	
	if coref:
		line = 	restore_coref(line, ref_dict)				#fix coref character
	
	
	if line[-1] != ')':                                 #skip dangling edges
		line = ")".join(line.split(')')[:-1]) + ')'
	
	line = add_space_when_digit(line, ['ARG','op','snt','-'])
	
	
	line = line.rstrip().lstrip(' \xef\xbb\xbf\ufeff')
	old_line = line
	line = line.rstrip().lstrip('> ')
	if len(old_line) > len(line):
	  print()
	
	if not (line == '(gm/gm' or line == ' :gs ' or line == ')') :
		line = convert(line)
	
	line = do_extra_steps(line)
	
	if coref:
		line = add_coref(line)		#now actually replace the 'coref-' nodes with the reference
	
	#if validator_seq2seq.valid_amr(line):
	#	print 'Valid'
	#else:
	#	print 'Invalid'	
	
	print line.strip()

