# D-match: evaluating scoped meaning representations

D-match is a tool that is able to evaluate scoped meaning representations, in this case Discourse Representation Graphs (DRGs). It compares sets of triples and outputs an F-score. The tool can be used to evaluate different DRG-parsers.
It is heavily based on [SMATCH](https://github.com/snowblink14/smatch), with a few modifications. It was developed as part of the [Parallel Meaning Bank](www.pmb.let.rug.nl).

## Getting Started

```
git clone https://github.com/RikVN/D-match
```

### Prerequisites

D-match runs with Python 2.7. The memory component needs [psutil](https://pypi.python.org/pypi/psutil).

## Differences with SMATCH ##

* D-match takes triples directly as input
* D-match can process multiple DRGs in parallel
* D-match can average over multiple runs of the system
* D-match needs more restarts, since DRGs, on average, have more triples and variables
* D-match can do baseline experiments, comparing a single DRG to a set of DRGs
* D-match can do sense experiments, e.g. ignoring sense or choosing a baseline sense
* D-match can use more smart initial mappings, based on concepts, names, variables order and initial matches
* D-match can print more detailed output, such as specific matching triples and F-scores for each smart mapping
* D-match can have a maximum number of triples for a single DRG, ignoring DRG-pairs with more triples
* D-match can have a memory limit per parallel thread
* Since DRGs have variable types, D-match ensures that different variable types can never match

## Running D-match

The most vanilla version can be run like this:

```
python d-match.py -f1 FILE1 -f2 FILE2
```

Running with our example data:

```
python d-match.py -f1 example_data/100_drgs.prod -f2 100_drgs.gold
```

### Parameter options ###

```
-f1   : First file with DRG triples, usually produced file
-f2   : Second file with DRG triples, usually gold file
-r    : Number of restarts used
-m    : Max number of triples for a DRG to still take them into account - default 0 means no limit
-p    : Number of parallel threads to use (default 1)
-runs : Number of runs to average over, if you want a more reliable result
-s    : What kind of smart initial mapping we use:
       'no'   : No smart mappings
       'order': Smart mapping based on order of the variables in the DRG (b1 maps to b1, b2 to b2, etc)
       'conc' : Smart mapping based on matching concepts (likely to be in the optimal mapping)
       'att'  : Smart mapping based on attribute triples (proper names usually), default
       'init' : Smart mapping based on number of initial matches for a set of mappings
       'freq' : Smart mapping based on frequency of the variables (currently not implemented)
-prin : Print more specific output, such as individual (avg) F-scores for the smart initial mappings, 
        and the matching and non-matching triples
-sense: Use this to do sense experiments
       'normal' : Don't change anything, just use triples as is (default)   
       'wrong'  : Always use the wrong sense for a concept; used to see impact of concept identification
       'ignore' : Ignore sense - meaning we always produced the correct sense
       'base'   : Always use the first sense for a concept (baseline)
-sig  : Number of significant digits to output (default 4)
-b    : Use this for baseline experiments, comparing a single DRG to a list of DRGs. 
        Produced DRG file should contain a single DRG.
-mem  : Memory limit per parallel thread in MBs, default 500        
-ms   : Instead of averaging the score, output a score for each DRG
-pr   : Also output precison and recall instead of only F-score
-v    : Verbose output
-vv   : Very verbose output  
```

### Running some tests ###

Run with 100 restarts, with 4 parallel threads to speed things up:

```
python d-match.py -f1 example_data/100_drgs.prod -f2 100_drgs.gold -r 100 -p 4
```

Print specific output, while only using the smart mapping based on concepts:

```
python d-match.py -f1 example_data/100_drgs.prod -f2 100_drgs.gold -r 100 -p 4 -prin -s conc
```

Only take smaller DRGs into account, with a maximum of 50 triples:

```
python d-match.py -f1 example_data/100_drgs.prod -f2 100_drgs.gold -r 100 -p 4 -prin -m 50
```

Doing a run that does not care about word sense disambuation:

```
python d-match.py -f1 example_data/100_drgs.prod -f2 100_drgs.gold -p 4 -prin -sense ignore
```

Outputting a score for each DRG (note we use -p 1 to not mess up printing):

```
python d-match.py -f1 example_data/100_drgs.prod -f2 100_drgs.gold -r 100 -p 1 -prin -ms
```

Doing a baseline experiment, comparing a single DRG to a number of DRGs:

```
python d-match.py -f1 example_data/single_drg.prod -f2 100_drgs.gold -r 100 -p 4 -prin --baseline
```

## Author

* **Rik van Noord** - PhD-student at University of Groningen - [Personal website](www.rikvannoord.nl)

## Paper ##

We are currently publishing a paper regarding D-match, once published the reference will be here.

## Acknowledgments

* Thanks to [SMATCH](https://github.com/snowblink14/smatch) for publishing their code open source.
* All members of the [Parallel Meaning Bank](www.pmb.let.rug.nl)
