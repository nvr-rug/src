#! /usr/bin/env python
import sys
import re


def countparens(text):
  ''' proper nested parens counting '''
  currcount=0
  for i in text:
    if i == "(":
      currcount+=1
    elif i == ")":
      currcount-=1
      if currcount < 0:
        return False
  return currcount == 0


def valid_amr(amrtext):
  import amr
  
  if not countparens(amrtext):		## wrong parentheses, return false
	  return False
  
  try:
	theamr = amr.AMR.parse_AMR_line(amrtext)
	if theamr is None:
	  return False
	  print "MAJOR WARNING: couldn't build amr out of "+amrtext+" using smatch code"
	else:
	  return True  

  except (AttributeError,Exception),e:
	#print 'Error:',e
	return False
  
  return True


