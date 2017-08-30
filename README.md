# Pre- and post-processing scripts for neural sequence-to-sequence AMR parsing

This repository contains a list of scripts that help in pre- and post-processing for neural AMR parsing. It helps put the AMR files into structures sequence-to-sequence models can handle. AMRs are converted to a single-line format, with variables and wiki-links removed. There are multiple options to handle co-referring nodes. There is also script that transforms the input AMR to best match the word order of the sentence. 

There are also scripts that put produced AMR files back in their original AMR format (restoring variables, wiki links).

## Getting Started

Simply clone the repository to your system to get started. All python programs are in Python2.7, not 3.

### Prerequisites

The Wikification script needs BeautifulSoup to work.

## Running the scripts

There are two main components of this repository: pre-processing the input and post-processing the output.

### Pre-processing

There are 4 different scripts to change the usual AMR format to single-line format without variables and Wiki-links. The default one is var_free_amrs.py and handles coreference by duplicating the co-referring nodes.

```
python var_free_amrs.py -f sample_input/sample.txt
```

There are two scripts that handle co-reference, either by using the Absolute Paths method or the Indexing method.

```
python create_coref_paths.py -f sample_input/sample.txt -p abs
```

```
python create_coref_indexing.py -f sample_input/sample.txt
```

The last script is similar to var_free_amrs.py, but swaps different AMR branches to best match the word order of the sentence. **This script needs the aligned AMRs as input!** By using the option -double, both the best aligned and original AMR are added in the dataset.

```
python best_amr_permutation.py -f sample_alignment_input/sample.txt
```

### Post-processing

The post-processing script are used to restore the variables and wiki-links, while also possibly handling the coreference nodes. There are individual scripts that can do each step, but they are combined in postprocess_AMRs.py. This script first restores the variables, by using a modified restoring script from [Didzis Gosko](https://github.com/didzis/tensorflowAMR/tree/master/SemEval2016/restoreAMR). Then, duplicate nodes are pruned (common problem when parsing) and coreference is put back (when duplicating that is, for Abs and Index method this is done in the restoring step). Finally, Wikipedia links are restored using Spotlight. These steps are done separately (creating .restore, .prune, .coref and .wiki files), but also together (creating .all file).

```
python postprocess_AMRs.py -f sample_alignment_input/sample.char.tf -s sample_alignment_input/sample.sent -o sample_input/
```

Here -f is the file to be processed, -s is the sentence file (needed for Wikification) and -o is the output directory to put the files. It is possible to use -no_wiki to skip the Wikification step.

## Important ##

* All scripts are AMR-specific, meaning that they are very reliant on the gold standard AMR formatting.
* This is **only** for pre- and post-processing, **not training and testing!** I recommend [OpenNMT](http://opennmt.net/) as a library for doing the actual experiments. All parameter settings can be found in the papers described below.


## Papers ##

Please see the following papers for details. For general AMR parsing methods:

* *Neural Semantic Parsing by Character-based Translation: Experiments with Abstract Meaning Representations*, Rik van Noord & Johan Bos, Accepted in CLiN 2017 Journal. [[PDF]](https://arxiv.org/pdf/1705.09980.pdf)

For coreference-specific information:

* *Dealing with Co-reference in Neural Semantic Parsing*, Rik van Noord & Johan Bos, To appear in IWCS Workshop SemDeep-2, Montpellier, 2017.

## About the Author

**Rik van Noord**, PhD student at University of Groningen, supervised by Johan Bos. Please see my [Personal website](http://rikvannoord.nl/) for more information. I'm happy to answer questions.
