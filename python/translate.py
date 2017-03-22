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
import json
from multiprocessing import Pool
from multiprocessing import Lock

import tensorflow.python.platform

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

import data_utils
import seq2seq_model
from tensorflow.python.platform import gfile

#import psutil # doesn't work on Peregrine

#parser = argparse.ArgumentParser()
#parser.add_argument("-t", required=True, type=str, help="file that contains the training instances")
#parser.add_argument("-ts", required=True, type=str, help="file that contains the testing")
#args = parser.parse_args()

tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 16,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("max_checkpoints", 100, "Maximum number of checkpoints we keep in the folder")
tf.app.flags.DEFINE_integer("max_threads", 5, "Maximum number of files we do in parallel")
tf.app.flags.DEFINE_integer("size", 400, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 1, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("en_vocab_size", 10, "English vocabulary size.")
tf.app.flags.DEFINE_integer("fr_vocab_size", 10, "French vocabulary size.")
tf.app.flags.DEFINE_integer("min_vocab", 1, "Min frequency of vocab items to be added in vocabulary")
tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "/tmp", "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("save_folder_checkpoint", 1,
                            "How often do we create a model folder per checkpoint file (1 is every checkpoint, 2 is every other checkpoint, 10 is once in 10 checkpoints, etc")
tf.app.flags.DEFINE_integer("eps_per_checkpoint", 1,
                            "How many training epochs to do per checkpoint.")
tf.app.flags.DEFINE_boolean("decode", False,
                            "Set to True for interactive decoding.")
tf.app.flags.DEFINE_boolean("buckets", False,
                            "Set to True using different buckets.")
tf.app.flags.DEFINE_boolean("self_test", False,
                            "Run a self-test if this is set to True.")
tf.app.flags.DEFINE_boolean("multiple_files", False,
                            "Test multiple files instead of just one")
tf.app.flags.DEFINE_string("train_file", "false","Train file (required!). Only use the text without suffixes, so argument is not an actual file")
tf.app.flags.DEFINE_string("test_file", "false", "Test file (required!). Only use the text without suffixes, so argument is not an actual file")
tf.app.flags.DEFINE_string("input_ext", ".sent", "Input extension of train/test files (default .sent)")
tf.app.flags.DEFINE_string("output_ext", ".tf", "Output extension of train/test files (default .tf)")
tf.app.flags.DEFINE_string("test_ext", ".char.sent", "Extension of the to-be-tested files (default .char.sent")
tf.app.flags.DEFINE_string("prod_ext", ".seq.amr", "Extension of the produced files (default .seq.amr")
tf.app.flags.DEFINE_string("checkpoint_dest", 'false', "Destination of checkpoints (required)")
tf.app.flags.DEFINE_string("log_file", '', "Logfile to write output to")
tf.app.flags.DEFINE_integer("stop_training", 0,
                            "Stop training after X epochs without improvement (0 means going indefinitely)")

## testing

tf.app.flags.DEFINE_string("decode_file", "false", "Actual test file for decoding")
tf.app.flags.DEFINE_string("out_file", "false", "File where the output is put (when just 1 testing)")
tf.app.flags.DEFINE_string("out_folder", "false", "Folder where the output is put (when multiple testing)")
tf.app.flags.DEFINE_string("test_folder", "false", "Folder with all the to be processed files")


FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
# _buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]
if FLAGS.buckets:   
    _buckets = [(510,510)]
else:
    
    _buckets = [(480, 480)]


def read_data(source_path, target_path, max_size=None):
  """Read data from source and target files and put into buckets.
  Args:
    source_path: path to the files with token-ids for the source language.
    target_path: path to the file with token-ids for the target language;
      it must be aligned with the source file: n-th line contains the desired
      output for n-th line from the source_path.
    max_size: maximum number of lines to read, all other will be ignored;
      if 0 or None, data files will be read completely (no limit).
  Returns:
    data_set: a list of length len(_buckets); data_set[n] contains a list of
      (source, target) pairs read from the provided data files that fit
      into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
      len(target) < _buckets[n][1]; source and target are lists of token-ids.
  """
  data_set = [[] for _ in _buckets]
  no_append = 0
  possible_buckets = [0,0]
  
  with gfile.GFile(source_path, mode="r") as source_file:
    with gfile.GFile(target_path, mode="r") as target_file:
      source, target = source_file.readline(), target_file.readline()
      counter = 0
      while source and target and (not max_size or counter < max_size):
        counter += 1
        if counter % 100000 == 0:
          print("  reading data line %d" % counter)
          sys.stdout.flush()
        source_ids = [int(x) for x in source.split()]
        target_ids = [int(x) for x in target.split()]
        target_ids.append(data_utils.EOS_ID)
        found_bucket = False
        
        for bucket_id, (source_size, target_size) in enumerate(_buckets):
          if len(source_ids) < source_size and len(target_ids) < target_size:
            data_set[bucket_id].append([source_ids, target_ids])
            found_bucket = True
            possible_buckets[bucket_id] += 1
            break
        if not found_bucket:
            possible_buckets[len(_buckets)] += 1       
             
        source, target = source_file.readline(), target_file.readline()
        
  print ('Bucket division {0}'.format(possible_buckets))
  #print ('No append {0}'.format(no_append))
  return data_set

#def print_mem_usage(current_step):          ## doesn't work on peregrine
 #   process = psutil.Process(os.getpid())
  #  bytes_mem = process.memory_info().rss
   # print ('Step',str(current_step) + ':', 'mem usage:', str(bytes_mem/(1000*1000*1000)), 'GB')


def get_restore_path(ckpt_path):
	if ckpt_path.count('/') > 2:					#peregrine
		restore_path = ckpt_path
	elif FLAGS.train_dir.endswith('/'):				#zardoz/johan, forgot slash
		restore_path = FLAGS.train_dir + ckpt_path
	else:
		restore_path = FLAGS.train_dir + '/' + ckpt_path
	
	print ('Restore path: {0}'.format(restore_path))
	return restore_path	


def create_model_test(session, forward_only):
  """Create translation model and initialize or load parameters in session."""
  model = seq2seq_model.Seq2SeqModel(
      FLAGS.en_vocab_size, FLAGS.fr_vocab_size, _buckets,
      FLAGS.size, FLAGS.num_layers, FLAGS.max_gradient_norm, FLAGS.batch_size,
      FLAGS.learning_rate, FLAGS.learning_rate_decay_factor,
      forward_only=forward_only, max_checkpoints = FLAGS.max_checkpoints)
  ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
  print ('ckpt:', ckpt)
  #if ckpt and gfile.Exists(ckpt.model_checkpoint_path):
  
  print ('model path:',ckpt.model_checkpoint_path)
  
  restore_path = get_restore_path(ckpt.model_checkpoint_path)
  
  if ckpt and os.path.exists(restore_path):
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model.saver.restore(session, restore_path)
  else:
    print("Created model with fresh parameters.")
    session.run(tf.initialize_all_variables())
  return model
  
def create_model_train(session, forward_only):
  """Create translation model and initialize or load parameters in session."""
  model = seq2seq_model.Seq2SeqModel(
      FLAGS.en_vocab_size, FLAGS.fr_vocab_size, _buckets,
      FLAGS.size, FLAGS.num_layers, FLAGS.max_gradient_norm, FLAGS.batch_size,
      FLAGS.learning_rate, FLAGS.learning_rate_decay_factor,
      forward_only=forward_only, max_checkpoints = FLAGS.max_checkpoints)
  
  ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
  print ('Creating model...')
  if ckpt:
    restore_path = get_restore_path(ckpt.model_checkpoint_path)
      
    print ('restore_path', restore_path)
    if ckpt and os.path.exists(restore_path):
      print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
      model.saver.restore(session, restore_path)
      if os.path.isfile(FLAGS.checkpoint_dest + 'perplexity_list.json'):
          with open(FLAGS.checkpoint_dest + 'perplexity_list.json', 'r') as in_f:
              ppxy = json.load(in_f)
          in_f.close()    
      else:
          print("Training from checkpoint but no perplexity file found")
          ppxy = []               
    else:
      print("Created model with fresh parameters.")
      session.run(tf.initialize_all_variables())
      ppxy = []
  else:
    print("Created model with fresh parameters.")
    session.run(tf.initialize_all_variables())
    ppxy = []  
  return model, ppxy
  
 
  #print ('ckpt:', ckpt.model_checkpoint_path)
  #if ckpt and gfile.Exists(ckpt.model_checkpoint_path):
    #print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    #model.saver.restore(session, ckpt.model_checkpoint_path)
  #else:
    #print("Created model with fresh parameters.")
    #session.run(tf.initialize_all_variables())
  
  #return model    

def save_checkpoint_check(train_size, eps_per_checkpoint, batch_size, instances_seen):
    if instances_seen < batch_size:     # no issues when 0 instances seen
        return False
    
    for idx in range(instances_seen, instances_seen + batch_size):  # due to batch_size we do not always test each instance and thus need this forloop
        save_num = int(train_size * eps_per_checkpoint)             # if we did eps_per_checkpoints epochs, we return True
        if idx % save_num == 0:
            return True
    
    return False        

def save_folder(model, batch_size):
    f_name = "translate.ckpt-" + str( model.global_step.eval() * batch_size)
    os.system('mkdir {0}dir_{1}'.format(FLAGS.checkpoint_dest, f_name))           # create folder for checkpoint
    os.system('mv {0}{1} {0}dir_{1}/'.format(FLAGS.checkpoint_dest, f_name))         # move checkpoint file to its folder
    os.system('mv {0}{1}.meta {0}dir_{1}/'.format(FLAGS.checkpoint_dest, f_name))        # move meta file to its folder
    
    with open(FLAGS.checkpoint_dest +  'dir_' + f_name + '/' + 'checkpoint', 'w') as f:       # create checkpoint description file            
        f.write('model_checkpoint_path: "{0}"\n'.format(f_name))
        f.write('all_model_checkpoint_paths: "{0}"'.format(f_name))
    f.close()   
        
        
def train():
  """Train the seq2seq model"""
    
  # Prepare data.
  print("Preparing data in %s" % FLAGS.data_dir)
  en_train, fr_train, en_dev, fr_dev, _, _ = data_utils.prepare_data(
      FLAGS.data_dir, FLAGS.en_vocab_size, FLAGS.fr_vocab_size, FLAGS.train_file, FLAGS.test_file, FLAGS.input_ext, FLAGS.output_ext, FLAGS.min_vocab)
  print ('Input ext:', FLAGS.input_ext)
  print ('Output ext:', FLAGS.output_ext)
  #with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:   #use this to see if GPU works
  #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
  #with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
  with tf.Session() as sess:
    # Create model.
    print("Creating %d layers of %d units." % (FLAGS.num_layers, FLAGS.size))
    model, ppxy = create_model_train(sess, False)
    # Read data into buckets and compute their sizes.
    print ("Reading development and training data (limit: %d)."
           % FLAGS.max_train_data_size)
    dev_set = read_data(en_dev, fr_dev)
    train_set = read_data(en_train, fr_train, FLAGS.max_train_data_size)
    train_bucket_sizes = [len(train_set[b]) for b in xrange(len(_buckets))]
    train_total_size = float(sum(train_bucket_sizes))
    print ('Total train size: {0}'.format(train_total_size))
    print ('Batch size: {0}'.format(FLAGS.batch_size))
    
    # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
    # the size if i-th training bucket, as used later.
    train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                           for i in xrange(len(train_bucket_sizes))]
    # This is the training loop.
    loss = 0.0
    current_step = 0
    instances_seen = model.global_step.eval() * FLAGS.batch_size
    previous_losses = []
    time_prev = timeit.default_timer()
    epochs = 0
    cps_counter = 0
    previous_ppx = 100000000
    no_improvement = 0
    keep_training = True
    #for var in tf.trainable_variables():
    #   print (var.name)
    while keep_training:
      # Choose a bucket according to data distribution. We pick a random number
      # in [0, 1] and use the corresponding interval in train_buckets_scale.
      #print ('Current step {0}'.format(current_step))
      random_number_01 = np.random.random_sample()
      bucket_id = min([i for i in xrange(len(train_buckets_scale))
                       if train_buckets_scale[i] > random_number_01])

      # Get a batch and make a step.
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          train_set, bucket_id)
      _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                   target_weights, bucket_id, False)
      loss += step_loss / ((train_total_size * FLAGS.eps_per_checkpoint) / FLAGS.batch_size)
      current_step += 1
      
      # Once in a while, we save checkpoint, print statistics, and run evals.
      #if current_step % FLAGS.steps_per_checkpoint == 0:
      if save_checkpoint_check(train_total_size, FLAGS.eps_per_checkpoint, FLAGS.batch_size, instances_seen):
        cps_counter += 1
        epochs += FLAGS.eps_per_checkpoint
        print ('Saving checkpoint for epochs {0} step {1} and instances seen {2}'.format(epochs, current_step, instances_seen))
        # Print statistics for the previous epoch.
        perplexity = math.exp(loss) if loss < 300 else float('inf')
        #print ("Epochs %d Instances seen %d learning rate %.4f perplexity "
               #"%.2f" % (epochs, instances_seen, model.learning_rate.eval(), perplexity))
        # Decrease learning rate if no improvement was seen over last 3 times.
        if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
          sess.run(model.learning_rate_decay_op)
        previous_losses.append(loss)
        # Save checkpoint and zero timer and loss.
        checkpoint_path = os.path.join(FLAGS.train_dir, "translate.ckpt")
        #model.saver.save(sess, checkpoint_path, global_step=model.global_step.eval() * FLAGS.batch_size)
        loss = 0.0
        # Run evals on development set and print their perplexity.
        for bucket_id in xrange(len(_buckets)):
          encoder_inputs, decoder_inputs, target_weights = model.get_batch(
              dev_set, bucket_id)
          _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, True)
          eval_ppx = math.exp(eval_loss) if eval_loss < 300 else float('inf')
          #print("  eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))
          time_now = timeit.default_timer()
          #print (str(float((time_now - time_prev)) / float(60)),'minutes for testing', str(FLAGS.eps_per_checkpoint),'epochs of ' + str(int(train_total_size)) + ' instances')
          time_prev = timeit.default_timer()
          
          #save perplexity information (training and dev) to file
          #print ('Print perplexities to json file')
          ppxy.append([perplexity, eval_ppx, current_step, epochs])
          with open(FLAGS.checkpoint_dest + 'perplexity_list.json', 'w') as out_f:
            json.dump(ppxy, out_f)
          out_f.close()  
                
          #if cps_counter % FLAGS.save_folder_checkpoint == 0:
          #    print ('Saving folder for step {0} and epoch {1}'.format(current_step, epochs))
          #    save_folder(model, FLAGS.batch_size)
          #    cps_counter = 0
        
        if round(eval_ppx,2) < previous_ppx:        #keep track of number of times we did not improve
            no_improvement = 0
            print ('Improvement, {0} vs {1}'.format(round(eval_ppx,2), previous_ppx))
        else:
            no_improvement += 1
            print ('No improvement, {0} vs {1}'.format(round(eval_ppx,2), previous_ppx))
        
        print('stop_training = {0}'.format(int(FLAGS.stop_training)))
        if no_improvement >= int(FLAGS.stop_training) and int(FLAGS.stop_training) > 0:
            print ('Stop training, no_improvement = {0}'.format(no_improvement))
            keep_training = False       #stop training after X epochs of no improvement
        
        print ('Current no improvement count {0}'.format(no_improvement))
        previous_ppx = round(eval_ppx,2)
                  
        
        sys.stdout.flush()
      instances_seen += FLAGS.batch_size

def decode_file(decode_file, out_file, en_vocab,rev_fr_vocab, sess, model):
    sentences = [x for x in open(decode_file,'r')]
    count = 0
    
    with open(decode_file,'r') as f:
        with open(out_file,'w') as out_f:
            for idx, sentence in enumerate(sentences):
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
                    # Print out French sentence corresponding to outputs.
                    #print (outputs)
                    #print ('len vocab:', len(rev_fr_vocab))
                    out = " ".join([rev_fr_vocab[output] for output in outputs])
                    #print ('sent:', sentence)
                    #print ('amr:',out.replace(' ','').replace('+',' '),'\n')
                    #print ('input:\n')
                    #print (sentence,'\noutput:\n')
                   #print ((out.replace(' ','').replace('+',' ')) + '\n\n') 
                    out_f.write((out.replace(' ','').replace('+',' ')) + '\n')
                else:
                    #print (outputs)
                    #print ('len vocab:', len(rev_fr_vocab))
                    out = " ".join([rev_fr_vocab[output] for output in outputs])
                    #print ((out.replace(' ','').replace('+',' ')) + '\n')  
                    out_f.write((out.replace(' ','').replace('+',' ')) + '\n')  
        print ('Done with {0}'.format(decode_file))         
    out_f.close()
    f.close()               


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
    
    if FLAGS.multiple_files:                      #save files and path
        for root, dirs, files in os.walk(FLAGS.test_folder):
            for f in files:
                if f.endswith(FLAGS.test_ext):
                    out_file = FLAGS.out_folder + '/' + f.replace(FLAGS.test_ext,FLAGS.prod_ext)       # create output with different extension
                    d_file = os.path.join(root, f)
                    decode_file(d_file, out_file, en_vocab, rev_fr_vocab, sess, model)
    else:
        decode_file(FLAGS.decode_file, FLAGS.out_file, en_vocab, rev_fr_vocab, sess, model)
   
    #max_processes = min(FLAGS.max_threads, len(arg_list))
    #pool = Pool(processes=max_processes)    
    #pool.map(decode_file, arg_list)     


def self_test():
  """Test the translation model."""
  with tf.Session() as sess:
    print("Self-test for neural translation model.")
    # Create model with vocabularies of 10, 2 small buckets, 2 layers of 32.
    model = seq2seq_model.Seq2SeqModel(10, 10, [(3, 3), (6, 6)], 32, 2,
                                       5.0, 32, 0.3, 0.99, num_samples=8, max_checkpoints = FLAGS.max_checkpoints)
    sess.run(tf.initialize_all_variables())

    # Fake data set for both the (3, 3) and (6, 6) bucket.
    data_set = ([([1, 1], [2, 2]), ([3, 3], [4]), ([5], [6])],
                [([1, 1, 1, 1, 1], [2, 2, 2, 2, 2]), ([3, 3, 3], [5, 6])])
    for _ in xrange(5):  # Train the fake model for 5 steps.
      bucket_id = random.choice([0, 1])
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          data_set, bucket_id)
      model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                 bucket_id, False)


def main(_):
  if FLAGS.self_test:
    self_test()
  elif FLAGS.decode:
    #if FLAGS.log_file:
     # sys.stdout = open(FLAGS.log_file,'a')
    decode()
  else:
    train()

if __name__ == "__main__":
  tf.app.run()
