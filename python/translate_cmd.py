# Copyright 2015 Google Inc. All Rights Reserved.
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Binary for training translation models and decoding from them.
Running this program without --decode will download the WMT corpus into
the directory specified as --data_dir and tokenize it in a very basic way,
and then start training a model saving checkpoints to --train_dir.
Running with --decode starts an interactive loop so you can see how
the current checkpoint translates English sentences into French.
See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/pdf/1412.2007v2.pdf
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time
import timeit
import argparse
from multiprocessing import Pool
from multiprocessing import Lock

import tensorflow.python.platform

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

import data_utils
import seq2seq_model
from tensorflow.python.platform import gfile

import psutil # doesn't work on Peregrine
sys.path.insert(0, '/home/p266548/Documents/amr_Rik/Seq2seq/src/python/restoreAMR/')


tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 16,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 400, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 1, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("en_vocab_size", 140, "English vocabulary size.")
tf.app.flags.DEFINE_integer("fr_vocab_size", 140, "French vocabulary size.")
tf.app.flags.DEFINE_integer("max_checkpoints", 100, "French vocabulary size.")
tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "/tmp", "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_boolean("buckets", False,
                            "Set to True using different buckets.")
tf.app.flags.DEFINE_string("input_ext", ".char.sent.pos", "Data directory")
tf.app.flags.DEFINE_string("output_ext", ".char.tf", "Training directory.")



FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
# _buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]
if FLAGS.buckets:   
    _buckets = [(510,510)]
else:
    
    _buckets = [(480, 480)]


def write_to_file(f,l):
	with open(f, 'w') as out_f:
		out_f.write(l.strip() + '\n')
	out_f.close()	


def nice_print_amr(line):
	prev_ch = ''
	fixed_amrs = []
	num_tabs = 0
	amr_string = ''
	
	for ch in line:
		if ch == '(':
			num_tabs += 1
			amr_string += ch
		elif ch == ')':
			num_tabs -= 1
			amr_string += ch
		elif ch	 == ':':	
			if prev_ch == ' ':	#only do when prev char is a space, else it was probably a HTML link or something
				amr_string += '\n' + num_tabs * '\t' + ch
			else:
				amr_string += ch	
		else:
			amr_string += ch
		prev_ch = ch
			
	print (amr_string)


def char_level_pos(line):
	new_l = ''
	no_spaces = False
	line = line.replace(' ','+') #replace actual spaces with '+'
	
	for idx, ch in enumerate(line):
		if ch == '|':
			no_spaces = True	#skip identifier '|' in the data
			new_l += ' '
		elif ch == ':' and line[idx-1] == '|':	#structure words are also chunks
			no_spaces = True
		elif ch == '+':
			no_spaces = False
			new_l += ' ' + ch
		elif no_spaces: #and (ch.isupper() or ch == '$'):		#only do no space when uppercase letters (VBZ, NNP, etc), special case PRP$	(not necessary)
			new_l += ch
		else:
			new_l += ' ' + ch
	return new_l

def postag_line(line):
	f_path = 'temp.txt'
	write_to_file(f_path,line)
	os_call = "cat {0} | sed -e 's/|/\//g' | sed 's/^ *//;s/ *$//;s/  */ /g;' | /net/gsb/pmb/ext/candc/bin/pos --model /net/gsb/pmb/ext/candc/models/boxer/pos/ --output {1} --maxwords 5000".format(f_path, f_path + '.pos_temp')
	os.system(os_call)
	
	#repl puncuation POS-tags
	
	repl_call = "cat {0} | sed 's/,|,/,/g' | sed 's/\.|\./\./g' | sed 's/!|\./!/g' | sed 's/;|;/;/g' | sed 's/-|:/-/g' | sed 's/:|:/:/g' > {1}".format(f_path + '.pos_temp', f_path + '.pos')
	os.system(repl_call)
	postagged_line = [x.strip() for idx, x in enumerate(open(f_path + '.pos', 'r')) if idx == 0][0]
	print (postagged_line)
	os.system('rm {0}'.format(f_path))
	os.system('rm {0}'.format(f_path + '.pos'))
	os.system('rm {0}'.format(f_path + '.pos_temp'))
	return postagged_line


def print_mem_usage(current_step):          ## doesn't work on peregrine
    process = psutil.Process(os.getpid())
    bytes_mem = process.memory_info().rss
    print ('Step',str(current_step) + ':', 'mem usage:', str(bytes_mem/(1000*1000*1000)), 'GB')

def create_model_test(session, forward_only):
  """Create translation model and initialize or load parameters in session."""
  model = seq2seq_model.Seq2SeqModel(
      FLAGS.en_vocab_size, FLAGS.fr_vocab_size, _buckets,
      FLAGS.size, FLAGS.num_layers, FLAGS.max_gradient_norm, FLAGS.batch_size,
      FLAGS.learning_rate, FLAGS.learning_rate_decay_factor,
      forward_only=forward_only, max_checkpoints = FLAGS.max_checkpoints)
  ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
  #print ('ckpt:', ckpt)
  #if ckpt and gfile.Exists(ckpt.model_checkpoint_path):
  
  #print ('model path:',ckpt.model_checkpoint_path)
  
  #if FLAGS.train_dir.endswith('/'):
  #  restore_path = FLAGS.train_dir + ckpt.model_checkpoint_path
  #else:
  #  restore_path = FLAGS.train_dir + '/' + ckpt.model_checkpoint_path
  
  restore_path = ckpt.model_checkpoint_path
  
  #print ('restore_path', restore_path)
  if ckpt and os.path.exists(restore_path):
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model.saver.restore(session, restore_path)
  else:
    print("Created model with fresh parameters.")
    session.run(tf.initialize_all_variables())
  return model
          
        
def decode_line(en_vocab,rev_fr_vocab, sess, model):
    
    sys.stdout.write("> ")
    sys.stdout.flush()
    sentence = sys.stdin.readline()
    while sentence:
        sentence = postag_line(sentence)
        sentence = char_level_pos(sentence)
        print ('\n')
        # Get token-ids for the input sentence.
        token_idsgb = data_utils.sentence_to_token_ids(sentence, en_vocab)
        # Truncate sentence to the maximum bucket size
        token_ids = token_idsgb[0:479]
        # Which bucket does it belong to?
        bucket_id = min([b for b in xrange(len(_buckets))
                       if _buckets[b][0] > len(token_ids)])
        # Get a 1-element batch to feed the sentence to the model.
        encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          {bucket_id: [(token_ids, [])]}, bucket_id)
        # Get output logits for the sentence.
        _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, True)
        # This is a greedy decoder - outputs are just argmaxes of output_logits.
        outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
        # If there is an EOS symbol in outputs, cut them at that point.
        if data_utils.EOS_ID in outputs:
            outputs = outputs[:outputs.index(data_utils.EOS_ID)]
            out = " ".join([rev_fr_vocab[output] for output in outputs])
            sent = (out.replace(' ','').replace('+',' '))
        else:
            out = " ".join([rev_fr_vocab[output] for output in outputs])
            sent(out.replace(' ','').replace('+',' '))
        
        nice_print_amr(sent)     
        
        print("\n> ", end="")
        sys.stdout.flush()
        sentence = sys.stdin.readline()             


def decode():
  with tf.Session() as sess:
    # Create model and load parameters.
    model = create_model_test(sess, True)
    model.batch_size = 1  # We decode one sentence at a time.

    # Load vocabularies.
    en_vocab_path = os.path.join(FLAGS.data_dir,
                                 "vocab{0}{1}".format(FLAGS.en_vocab_size, FLAGS.input_ext))
    fr_vocab_path = os.path.join(FLAGS.data_dir,
                                 "vocab{0}{1}".format(FLAGS.fr_vocab_size, FLAGS.output_ext))
    en_vocab, _ = data_utils.initialize_vocabulary(en_vocab_path)
    _, rev_fr_vocab = data_utils.initialize_vocabulary(fr_vocab_path)
    

    decode_line(en_vocab, rev_fr_vocab, sess, model)


def main(_):
	decode()

if __name__ == "__main__":
  tf.app.run()
