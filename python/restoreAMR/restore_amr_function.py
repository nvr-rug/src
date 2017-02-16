#!/usr/bin/env python3

import sys, re, os, json
from trans import translate, restore

#def usage():
 #   print('usage:', sys.argv[0], '[--plain] [--apply-on <comment tag>] < input.amr > output.amr', file=sys.stderr)

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
    
    return new_line

def process_line(line):
	unbracket = re.compile(r'\(\s*([^():\s"]*)\s*\)')
	dangling_edges = re.compile(r':[\w\-]+\s*(?=[:)])')
	missing_edges = re.compile(r'(\/\s*[\w\-]+)\s+\(')
	missing_variable = re.compile(r'(?<=\()\s*([\w\-]+)\s+(?=:)')
	missing_quotes = re.compile(r'("\w+)(?=\s\))')
	misplaced_colon = re.compile(r':(?=\))')
	missing_concept_and_variable = re.compile(r'(?<=\()\s*(?=:\w+)')
	dangling_quotes = re.compile(r'(?<=\s)(\w+)"(?=\s|\)|:)')
	
	global ggg
	ggg = 1

	line = line.replace(' ','').replace('+',' ')
	
	if line[-1] != ')':                                 #skip dangling edges
		line = ")".join(line.split(')')[:-1]) + ')'
	
	line = add_space_when_digit(line, ['ARG','op','snt','-'])
	
	line = line.rstrip().lstrip(' \xef\xbb\xbf\ufeff')
	old_line = line
	line = line.rstrip().lstrip('> ')
	if len(old_line) > len(line):
	  print 'Error?'
	
	if not (line == '(gm/gm' or line == ' :gs ' or line == ')') :
		line = convert(line)
	
	line = do_extra_steps(line)
	return line.strip()


