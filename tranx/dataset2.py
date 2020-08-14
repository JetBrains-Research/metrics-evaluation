import argparse
import json
import os
import pickle
import sys

import signal
import time

import numpy as np

from asdl.hypothesis import *
from asdl.lang.py3.py3_transition_system import python_ast_to_asdl_ast, asdl_ast_to_python_ast, \
    Python3TransitionSystem
from asdl.transition_system import *
from components.action_info import get_action_infos
from components.dataset import Example
from components.vocab import Vocab, VocabEntry
from datasets.conala.evaluator import ConalaEvaluator
from datasets.conala.util import *

from joblib import Parallel, delayed
from tqdm import tqdm


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


assert astor.__version__ == '0.7.1'


def preprocess_conala_dataset(train_file, test_file, grammar_file, split, src_freq=3, code_freq=3,
                              mined_data_file=None, api_data_file=None,
                              vocab_size=20000, num_mined=0, out_dir='data/conala', n_jobs=1, n_files=20): 
    np.random.seed(1234)

    asdl_text = open(grammar_file).read()
    grammar = ASDLGrammar.from_text(asdl_text)
    transition_system = Python3TransitionSystem(grammar)

    print('process gold training data...')
    train_examples = preprocess_dataset(train_file, name='train',
                                        transition_system=transition_system, n_jobs=n_jobs)

    # held out (1-split)*len(train_examples) examples for development
    #full_train_examples = train_examples[:]
    # np.random.shuffle(train_examples)
    n_train_examples = int(split*len(train_examples))
    dev_examples = train_examples[n_train_examples:]
    train_examples = train_examples[:n_train_examples]

    mined_examples = []
    api_examples = []
    if mined_data_file and num_mined > 0:
        print("use mined data: ", num_mined)
        print("from file: ", mined_data_file)
        mined_examples = preprocess_dataset(mined_data_file, name='mined',
                                            transition_system=transition_system,
                                            firstk=num_mined, n_jobs=n_jobs)
        pickle.dump(mined_examples,
                    open(os.path.join(out_dir, 'mined_{}.bin'.format(num_mined)), 'wb'))

    if api_data_file:
        print("use api docs from file: ", api_data_file)
        name = os.path.splitext(os.path.basename(api_data_file))[0]
        api_examples = preprocess_dataset(api_data_file, name='api',
                                          transition_system=transition_system, n_jobs=n_jobs)
        pickle.dump(api_examples, open(os.path.join(out_dir, name + '.bin'), 'wb'))

    if mined_examples and api_examples:
        pickle.dump(mined_examples + api_examples,
                    open(os.path.join(out_dir, 'pre_{}_{}.bin'.format(num_mined, name)), 'wb'))

    # combine to make vocab
    train_examples += mined_examples
    train_examples += api_examples
    print(f'{len(train_examples)} training instances', file=sys.stderr)
    print(f'{len(dev_examples)} dev instances', file=sys.stderr)

    print('process testing data...')
    test_examples = preprocess_dataset(test_file, name='test', transition_system=transition_system,
                                       n_jobs=n_jobs)
    print(f'{len(test_examples)} testing instances', file=sys.stderr)

    src_vocab = VocabEntry.from_corpus([e.src_sent for e in train_examples], size=vocab_size,
                                       freq_cutoff=src_freq)
    primitive_tokens = [map(lambda a: a.action.token,
                            filter(lambda a: isinstance(a.action, GenTokenAction), e.tgt_actions))
                        for e in train_examples]
    primitive_vocab = VocabEntry.from_corpus(primitive_tokens, size=vocab_size,
                                             freq_cutoff=code_freq)

    # generate vocabulary for the code tokens!
    code_tokens = [transition_system.tokenize_code(e.tgt_code, mode='decoder') for e in
                   train_examples]

    code_vocab = VocabEntry.from_corpus(code_tokens, size=vocab_size, freq_cutoff=code_freq)

    vocab = Vocab(source=src_vocab, primitive=primitive_vocab, code=code_vocab)
    print('generated vocabulary %s' % repr(vocab), file=sys.stderr)

    action_lens = [len(e.tgt_actions) for e in train_examples]
    print('Max action len: %d' % max(action_lens), file=sys.stderr)
    print('Avg action len: %d' % np.average(action_lens), file=sys.stderr)
    print('Actions larger than 100: %d' % len(list(filter(lambda x: x > 100, action_lens))),
          file=sys.stderr)
    train_split = np.array_split(np.array(train_examples), n_files)
    for i, train_out in enumerate(train_split):
        pickle.dump(list(train_out),open(os.path.join(out_dir, f'train.all_{i}.bin'), 'wb'))
    pickle.dump(dev_examples, open(os.path.join(out_dir, 'dev.bin'), 'wb'))
    pickle.dump(test_examples, open(os.path.join(out_dir, 'test.bin'), 'wb'))
    if mined_examples and api_examples:
        vocab_name = 'vocab.src_freq%d.code_freq%d.mined_%s.%s.bin' % (
            src_freq, code_freq, num_mined, name)
    elif mined_examples:
        vocab_name = 'vocab.src_freq%d.code_freq%d.mined_%s.bin' % (src_freq, code_freq, num_mined)
    elif api_examples:
        vocab_name = 'vocab.src_freq%d.code_freq%d.%s.bin' % (src_freq, code_freq, name)
    else:
        vocab_name = 'vocab.src_freq%d.code_freq%d.bin' % (src_freq, code_freq)
    pickle.dump(vocab, open(os.path.join(out_dir, vocab_name), 'wb'))


def process_example_long(i, example_json, evaluator, transition_system):
    try:
        with timeout(seconds=10):
            snippet = example_json['snippet']
            #    snippet = 'def foo(): \n' + snippet
            snippet = snippet.replace('DCNL ', '\n')
            snippet = snippet.replace(' DCSP ', '    ')
            snippet = snippet.replace('DCSP ', '    ')
            snippet = snippet.replace('DCTB ', '    ')
            example_json['snippet'] = snippet
            example_dict = preprocess_example(example_json)
            #            print('success')
            python_ast = ast.parse(example_dict['canonical_snippet'])
            canonical_code = astor.to_source(python_ast).strip()
            tgt_ast = python_ast_to_asdl_ast(python_ast, transition_system.grammar)
            tgt_actions = transition_system.get_actions(tgt_ast)

            # sanity check
            hyp = Hypothesis()
            for t, action in enumerate(tgt_actions):
                assert action.__class__ in transition_system.get_valid_continuation_types(hyp)
                if isinstance(action, ApplyRuleAction):
                    assert action.production in transition_system.get_valid_continuating_productions(
                        hyp)
                # p_t = -1
                # f_t = None
                # if hyp.frontier_node:
                #     p_t = hyp.frontier_node.created_time
                #     f_t = hyp.frontier_field.field.__repr__(plain=True)
                #
                # # print('\t[%d] %s, frontier field: %s, parent: %d' % (t, action, f_t, p_t))
                hyp = hyp.clone_and_apply_action(action)

            assert hyp.frontier_node is None and hyp.frontier_field is None
            hyp.code = code_from_hyp = astor.to_source(
                asdl_ast_to_python_ast(hyp.tree, transition_system.grammar)).strip()
            # print(code_from_hyp)
            # print(canonical_code)
            assert code_from_hyp == canonical_code

            decanonicalized_code_from_hyp = decanonicalize_code(code_from_hyp,
                                                                example_dict['slot_map'])
            assert compare_ast(ast.parse(example_json['snippet']),
                               ast.parse(decanonicalized_code_from_hyp))
            assert transition_system.compare_ast(
                transition_system.surface_code_to_ast(decanonicalized_code_from_hyp),
                transition_system.surface_code_to_ast(example_json['snippet']))

            tgt_action_infos = get_action_infos(example_dict['intent_tokens'], tgt_actions)
    except (AssertionError, SyntaxError, ValueError, OverflowError, TimeoutError) as e:
        return None, example_json['question_id']

    example = Example(idx=f'{i}-{example_json["question_id"]}',
                      src_sent=example_dict['intent_tokens'],
                      tgt_actions=tgt_action_infos,
                      tgt_code=canonical_code,
                      tgt_ast=tgt_ast,
                      meta=dict(example_dict=example_json,
                                slot_map=example_dict['slot_map']))
    assert evaluator.is_hyp_correct(example, hyp)
    return example, None


def preprocess_dataset(file_path, transition_system, name='train', firstk=None, n_jobs=1):
    try:
        dataset = json.load(open(file_path))
    except:
        dataset = [json.loads(jline) for jline in open(file_path).readlines()]
    if firstk:
        dataset = dataset[:firstk]

    evaluator = ConalaEvaluator(transition_system)
    with Parallel(n_jobs=n_jobs) as pool:
        parallel_result = pool(
            delayed(process_example_long)(i, example_json, evaluator, transition_system)
            for i, example_json in tqdm(enumerate(dataset))
        )
        examples = [example for example, _ in parallel_result if example is not None]
        skipped_list = [skipped for _, skipped in parallel_result if skipped is not None]

    print('Skipped due to exceptions: %d' % len(skipped_list), file=sys.stderr)
    return examples


def preprocess_example(example_json):
    intent = example_json['intent']
    if 'rewritten_intent' in example_json:
        rewritten_intent = example_json['rewritten_intent']
    else:
        rewritten_intent = None

    if rewritten_intent is None:
        rewritten_intent = intent
    snippet = example_json['snippet']
    #    if os.path.exists('debug.txt'):
    #        with open('debug.txt', 'a') as o:
    #            o.write(snippet+'\n')
    #    else:
    #         with open('debug.txt', 'w') as o:
    #            o.write(snippet+'\n')

    #    print(snippet)

    canonical_intent, slot_map = canonicalize_intent(rewritten_intent)
    canonical_snippet = canonicalize_code(snippet, slot_map)
    intent_tokens = tokenize_intent(canonical_intent)
    decanonical_snippet = decanonicalize_code(canonical_snippet, slot_map)

    reconstructed_snippet = astor.to_source(ast.parse(snippet)).strip()
    reconstructed_decanonical_snippet = astor.to_source(ast.parse(decanonical_snippet)).strip()

    assert compare_ast(ast.parse(reconstructed_snippet),
                       ast.parse(reconstructed_decanonical_snippet))

    return {'canonical_intent': canonical_intent,
            'intent_tokens': intent_tokens,
            'slot_map': slot_map,
            'canonical_snippet': canonical_snippet}


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    #### General configuration ####
    arg_parser.add_argument('--pretrain', type=str, help='Path to pretrain file')
    arg_parser.add_argument('--out_dir', type=str, default='data/conala',
                            help='Path to output file')
    arg_parser.add_argument('--topk', type=int, default=0, help='First k number from mined file')
    arg_parser.add_argument('--freq', type=int, default=3, help='minimum frequency of tokens')
    arg_parser.add_argument('--vocabsize', type=int, default=20000,
                            help='First k number from pretrain file')
    arg_parser.add_argument('--include_api', type=str, help='Path to apidocs file')
    arg_parser.add_argument('--n_jobs', type=int, help='Number of threads to run preprocessing')
    arg_parser.add_argument('--n_files', type=int, default=40, help='Number of files to dump the train output in')
    arg_parser.add_argument('--train_file', type=str, default='docstrings-train.json', help='JSON file with train dataset')
    arg_parser.add_argument('--test_file', type=str, default='docstrings-test.json', help='JSON file with test dataset')
    #0.97959 corresponds to the 0.96/(0.96+0.02) split we chose
    arg_parser.add_argument('--split', type=float, default=0.97959, help='Ratio between train and dev parts') 
    args = arg_parser.parse_args()
    print(os.getcwd())

    preprocess_conala_dataset(train_file=args.train_file,
                              test_file=args.test_file,
                              mined_data_file=args.pretrain,
                              api_data_file=args.include_api,
                              grammar_file='asdl/lang/py3/py3_asdl.simplified.txt',
                              src_freq=args.freq, code_freq=args.freq,
                              vocab_size=args.vocabsize,
                              num_mined=args.topk,
                              out_dir=args.out_dir,
                              n_jobs=args.n_jobs,
                              n_files=args.n_files,
                              split=args.split)