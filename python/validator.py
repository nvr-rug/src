#! /usr/bin/env python
import argparse
import sys
import codecs
#from itertools import izip
from collections import defaultdict as dd
import re
import os.path
import gzip
scriptdir = os.path.dirname(os.path.abspath(__file__))


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



def main():
  parser = argparse.ArgumentParser(description="AMR validator",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--plainfile", "-p", nargs='?', type=argparse.FileType('r'), default=None, help="plain file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")
  parser.add_argument("--simple", "-s", action='store_true', default=False, help="Simple AMR validation. If you're having trouble, enable this to only do paren counting")

  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  if not args.simple:
    import amr

  reader = codecs.getreader('utf8')
  writer = codecs.getwriter('utf8')
  infile = gzip.open(args.infile.name, 'r') if args.infile.name.endswith(".gz") else args.infile
  infile = reader(infile)
  plainfile = None
  if args.plainfile is not None:
    plainfile = gzip.open(args.plainfile.name, 'r') if args.plainfile.name.endswith(".gz") else args.plainfile
    plainfile = reader(plainfile)

  outfile = gzip.open(args.outfile.name, 'w') if args.outfile.name.endswith(".gz") else args.outfile
  outfile = writer(outfile)


  buffer = []
  probcount=0
  amrcount = 0
  idset = set()
  sentset = set()
  sentcount = 0
  if plainfile is not None:
    for line in plainfile:
      if line.startswith("# ::id "):
        idset.add(line)
      elif line.startswith("# ::snt "):
        sentset.add(line)
#    if len(idset) != len(sentset):
#      outfile.write("Warning: %d ids but %d sentences; duplicate data?\n" % (len(idset), len(sentset)))
    sentcount = len(idset)
    origsentset = sentset.copy()
  for line in infile:
    # delete ids and snt texts seen in plainfile
    if plainfile is not None:
      if line.startswith("# ::id "):
        if line not in idset:
          outfile.write("Warning: found %s in amr file but not in (non-empty) plain file\n" % line.strip())
          probcount+=1
        else:
          idset.remove(line)
        continue
      elif line.startswith("# ::snt "):
        if line not in sentset:
          if line not in origsentset:
            outfile.write("Warning: found %s in amr file but not in (non-empty) plain file\n" % line.strip())
            probcount+=1
        else:
          sentset.remove(line)
        continue
    # hashtags can appear in amrs. only line-initial hash counts
    if line[0] == "#":
      continue
    line = line.strip()
    if (not line.isspace()) and len(line) > 0:
      buffer.append(line)
    else:
      if len(buffer) > 0:
        amrtext = ' '.join(buffer)
        amrcount += 1
        if not args.simple:
          try:
            theamr = amr.AMR.parse_AMR_line(amrtext)
            if theamr is None:
              raise Exception("MAJOR WARNING: couldn't build amr out of "+amrtext+" using smatch code")

          except (AttributeError,Exception),e:
            outfile.write(repr(e)+"\n")
            sys.exit(1)
            probcount+=1
        cleantext = re.sub(r"\"[^ ]+\"", "", amrtext)
        if not countparens(cleantext):
          outfile.write("MAJOR WARNING: parens not balanced in "+amrtext+"\n")
          sys.exit(1)
          probcount+=1
        buffer = []
  if len(buffer) > 0:
    amrtext = ' '.join(buffer)
    amrcount += 1
    if not args.simple:
      try:
        theamr = amr.AMR.parse_AMR_line(amrtext)
        if theamr is None:
          raise Exception("MAJOR WARNING: couldn't build amr out of "+amrtext+" using smatch code")
      except (AttributeError,Exception), e:
        outfile.write(repr(e)+"\n")
        sys.exit(1)
    cleantext = re.sub(r"\"[^ ]+\"", "", amrtext)
    if not countparens(cleantext):
      outfile.write("MAJOR WARNING: parens not balanced in "+amrtext+"\n")
      sys.exit(1)
  if probcount > 0:
    outfile.write("%d of %d amrs have a problem\n" % (probcount, amrcount))
  if len(idset) != 0:
    outfile.write("Warning: %d ids not seen in amr set (maybe you didn't include them? that's not necessarily a problem): Here is one:\n%s" % (len(idset), list(idset)[0]))
  if len(sentset) != 0:
    outfile.write("Warning: %d sents not seen in amr set (maybe you didn't include them? that's not necessarily a problem): Here is one:\n%s" % (len(sentset), list(sentset)[0]))

  if plainfile is not None:
    if amrcount != sentcount:
      outfile.write("MAJOR WARNING: %d amrs seen but %d expected\n" % (amrcount, sentcount))
    else:
      outfile.write("%d amrs expected and seen. Good sign!\n" % amrcount)
  else:
    outfile.write("%d amrs seen; pass a plainfile in to see how many are expected\n" % amrcount)
if __name__ == '__main__':
  main()

