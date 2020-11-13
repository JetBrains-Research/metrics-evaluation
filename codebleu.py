import tokenize
import re
import keyword
import json
from bleu_score import compute_bleu
import itertools
from collections import defaultdict 
from tree_sitter import Language, Parser

from io import BytesIO
from typing import List, Optional, Union, Any

keyword_weight = 4  #not sure about the keyword weight: in CodeBLEU paper it is 5 in one place and 4 in another. Real keyword_weight is keyword_weight + 1 (see e.g. realization in _dictize)
types = ('list', 'integer', 'float', 'dictionary', 'string')
comparison_ops = ('==', '!=', '>=', '<=', '<', '>')
assignment_ops = ('=', '-=', '+=')

#General functions
def _inlist(el, lst):
	if type(lst) == list:
		return el in lst
	else:
		return el == lst

def _find_prev(lst, num):
	if lst[0] > num:
		return -1
	elif lst[-1] <= num:
		return lst[-1]
	else:
		for i in range(len(lst) - 1):
			if lst[i] <= num < lst[i+1]:
				return lst[i]


#Data flow related part
def _find_all_variables(node, var_list, code):
	if node.type == 'identifier':
		id_name = code[node.start_byte:node.end_byte].decode('utf8')
		code_loc = node.start_byte
		to_append = True
		for item in var_list:
			if item[0] == id_name:
				item.append(code_loc)
				to_append = False
		if to_append:
			var_list.append([id_name, code_loc])
	for child in node.children:
		_find_all_variables(child, var_list, code)

def _identifiers_not_exist(node):
	if node.type  == 'identifier':
		return False
	if len(node.children) > 0:
		return all(list(map(_identifiers_exist, node.children)))
	else:
		return True

def _find_all_entities(node, exp_list, code, find_types, flatten=False):
	if find_types:
		if node.type in types and _identifiers_not_exist(node):
			exp_list.append((node.type, node.start_byte))
	elif node.type == 'identifier':
		id_name = code[node.start_byte:node.end_byte].decode('utf8')
		exp_list.append((id_name, node.start_byte))
	elif node.type == 'call' or node.type == 'list' or node.type == 'dictionary' or node.type == 'binary_operator':
		if not flatten: 
			sublist = list()
			for child in node.children:
				_find_all_entities(child, sublist, code, find_types, flatten=True)
			exp_list.append((sublist, node.start_byte))
	for child in node.children:
		_find_all_entities(child, exp_list, code, find_types)


def _normalize_variables(var_list):
	var_list.sort(key = lambda x: min(x[1:]))
	alias_dict = {item: item for item in types}
	for i, item in enumerate(var_list):
		alias_dict[item] = 'var'+str(i)
	return alias_dict

def _alias(item, alias_dict):
	if type(item) != list:
		return alias_dict[item]
	else:
		outlist = list()
		for itt in item:
			outlist.append(_alias(itt))
		return outlist


def _parse_expression(node, alias_dict, code, expressions_list, operators_list):
	for i, item in enumerate(node.children):
		if item.type in operators_list:
			break
	lhs = list()
	for item in node.children[:i]: #for the left-hand side of the assignment, we don't care about constants if they happen to appear there
		if node.type == 'comparison_operator':
			_find_all_entities(item, lhs, code, find_types = True)
		else:
			_find_all_entities(item, lhs, code, find_types = False)
	rhs = list()
	for item in node.children[i+1:]: # the right-hand side of the assignment, now everything matters
		_find_all_entities(item, rhs, code, find_types = True)
	lhs.sort(key = lambda x: x[1])
	rhs.sort(key = lambda x: x[1])
	if len(rhs) != len(lhs):
		raise Exception('LHS and RHS length mismatch')
	for l_item, r_item in lhs, rhs:
		expressions_list.append((_alias(l_item[0]), _alias(r_item[0]), l_item[1]))


def _find_expressions(node, alias_dict, code, assignments_list, comparisons_list):
	if node.type == 'assignment' or node.type == 'augmented_assignment':
		_parse_expression(node, alias_dict, code, assignments_list, assignment_ops)
	if node.type == 'comparison_operator':
		_parse_expression(node, alias_dict, code, comparisons_list, comparison_ops)
	for child in node.children:
		_find_expressions(child, alias_dict, code, assignments_list, comparisons_list)

def _find_data_sources(assignments_list):
	data_sources = dict()
	for item in assignments_list: #check if it is possible to get the list of variables on the lhs of the assignment
		if data_sources.get(item[0]) == None:
			data_sources[item[0]] = [item[2]]
		else:
			data_sources[item[0]].append(item[2])
	for key in data_sources:
		data_sources[key].sort()
	return data_sources

def _add_connection(item1, item2, code_loc, data_sources, is_assignment):
	outlist = list()	
	if is_assignment:
		if (type(item2) != list) and (item2 not in types):
			outlist.extend([[item1, item2, _find_prev(data_sources[item2], code_loc)]])
		else:
			for itt in item2:
				if itt not in types:
					outlist.extend([[item1, itt, _find_prev(data_sources[itt], code_loc)]])

	else:
		if (type(item2) != list) and (item2 not in types):
			outlist.extend([[item2, item2, _find_prev(data_sources[item2], code_loc)]])
		else:
			for itt in item2:
				if itt not in types:
					outlist.extend([[itt, itt, _find_prev(data_sources[itt], code_loc)]])
	return outlist

def _find_connections(assignments_list, comparisons_list):
	data_sources = _find_data_sources(assignments_list)
	connections_list = list()
	for item in comparisons_list:
		connections_list += _add_connection(item[0], item[0], item[2], data_sources, False) #lhs of the comparison
		connections_list += _add_connection(item[1], item[1], item[2], data_sources, False) #rhs of the comparison
	for item in assignments_list:
		connections_list += _add_connection(item[0], item[1], item[2], data_sources, True)
	return connections_list






#AST-related part
def _compare_nodes(node1, node2):
	return node1.type == node2.type

def _compare_ast(node1, node2):
	if not _compare_nodes(node1, node2):
		return False
	if len(node1.children) != len(node2.children):
		return False
	if len(node1.children) > 0:
		return all(itertools.starmap(_compare_ast, zip(node1.children, node2.children)))
	else:
		return True

def _find_subtrees(node, trees_list):
	trees_list.append(node)
	for item in node.children:
		_find_subtrees(item, trees_list)

def _comp_trees(ref_list, cand_list):
	common_subtrees = 0
	for cand_str in cand_list:
		for ref_str in ref_list:
			if _compare_ast(ref_str, cand_str):
				common_subtrees += 1
				ref_list.remove(ref_str)
				break
	return common_subtrees

def ast_match(reference, candidate, parser):
	try:
		ref_tree = parser.parse(bytes(reference, 'utf8'))
		cand_tree = parser.parse(bytes(candidate, 'utf8'))
	except:
		return -1
	ref_list = []
	cand_list = []
	_find_subtrees(ref_tree.root_node, ref_list)
	_find_subtrees(cand_tree.root_node, cand_list)
	#return ref_list, cand_list
	max_subtrees = len(ref_list)
	common_subtrees = _comp_trees(ref_list, cand_list)
	return max_subtrees, common_subtrees / max_subtrees

#The BLEU-related part

def _dictize(lst, kwd):
	out_dict = dict()
	for item in lst:
		out_dict[item] = out_dict.get(item, 0) + 1 + keyword_weight*_inlist(item, kwd)
	return out_dict

def _token_overlap(dict_ref, dict_can):
	matches = 0
	for key in dict_ref:
		matches += min(dict_ref[key], dict_can.get(key, 0))
	return matches

def tokenize_builtin(code: str) -> List[str]: #function by Egor Bogomolov
	try:
		tokens = list(tokenize.tokenize(BytesIO(code.encode('utf-8')).readline))[1:-1]
		tokens = [token.string for token in tokens]
		return tokens
	except tokenize.TokenError:
		return tokenize_tranx(code)

def tokenize_tranx(code: str) -> List[str]:
	""" The tokenizer taken from https://github.com/pcyin/tranX
		Originally from Wang Ling et al.,
		Latent Predictor Networks for Code Generation (2016)
		@param code: string containing a code snippet
		@return: list of code tokens
	"""
	code = re.sub(r'([^A-Za-z0-9_])', r' \1 ', code)
	code = re.sub(r'([a-z])([A-Z])', r'\1 \2', code)
	code = re.sub(r'\s+', ' ', code)
	code = code.replace('"', '`')
	code = code.replace('\'', '`')
	tokens = [t for t in code.split(' ') if t]

	return tokens

def pure_bleu(reference, candidate):
	return compute_bleu([tokenize_builtin(reference)], tokenize_builtin(candidate))

def weighted_bleu(reference, candidate):
	keywords = []
	for e in dir(__builtins__):
		keywords.append(e)
	for e in keyword.kwlist:
		keywords.append(e)

	ref_tokens = tokenize_builtin(reference)
	can_tokens = tokenize_builtin(candidate)
	ref_dict = _dictize(ref_tokens, keywords)
	can_dict = _dictize(can_tokens, keywords)

	ratio = len(can_tokens) / len(ref_tokens)
	if ratio > 1.0:
		bp = 1.
	else:
		if ratio == 0.:
			bp = 0.
		else:
			bp = math.exp(1 - 1. / ratio)

	possible_matches = 0
	for token in ref_tokens:
		possible_matches += 1 + keyword_weight*_inlist(token, keywords)
	matches = _token_overlap(ref_dict, can_dict)

	return matches * bp / possible_matches


def codebleu(reference, candidate):
	parser = Parser()
	PY_LANGUAGE = Language('my-languages.so', 'python')
	parser.set_language(PY_LANGUAGE)


"""The parts that didn't work out
# AST part of the metric
def _compare_ast(node1, node2):
	if type(node1) is not type(node2):
		return False
	if isinstance(node1, ast.AST):
		for k, v in vars(node1).items():
			if k in ('lineno', 'col_offset', 'ctx', 'end_lineno', 'end_col_offset'):
				continue
			if not _compare_ast(v, getattr(node2, k)):
				return False
		return True
	elif isinstance(node1, list):
		return all(itertools.starmap(_compare_ast, zip(node1, node2)))
	else:
		return node1 == node2

def _find_subtrees(node, trees_list):
	trees_list.append(node)
	if isinstance(node, ast.AST):
		for k, v in vars(node).items():
			if k in ('lineno', 'col_offset', 'ctx', 'end_lineno', 'end_col_offset'):
				continue
			_find_subtrees(v, trees_list)
		return True
	elif isinstance(node, list):
		for item in node:
			_find_subtrees(item, trees_list)
	else:
		pass


def ast_match(reference, candidate):
	try:
		ref_tree = ast.parse(reference)
		cand_tree = ast.parse(candidate)
	except:
		return -1
#	ref_tree = _ast_to_tree(ref_ast)
#	cand_tree = _ast_to_tree(cand_ast)
	ref_list = []
	cand_list = []
	_find_subtrees(ref_tree, ref_list)
	_find_subtrees(cand_tree, cand_list)
	#return ref_list, cand_list
	max_subtrees = len(ref_list)
	common_subtrees = _comp_trees(ref_list, cand_list)
	return max_subtrees, common_subtrees / max_subtrees

class Node(object):
	def __init__(self, data):
		self.data = data
		self.children = []

	def add_child(self, obj):
		self.children.append(obj)

#For some reason authors of CodeBLEU claim we need to leave out all leaves of the AST (which from the Figure 1 seems to mean "make all the leave values identical"); not sure that I understand why... Maybe gotta ditch this later
def _delete_leaves(node): 
	try:
		if len(node.children) > 0:
			for child in node.children:
				_delete_leaves(child)
		else:
			node.data = 'foo'
	except:
		node.data = 'foo'

def _comp_trees(ref_dict, cand_dict):
	common_subtrees = 0
	for key in cand_dict:
		common_subtrees += min(ref_dict[key], cand_dict[key])
	return common_subtrees

#I didn't understand how to work with AST (all the walking functions etc. seemed to be very unwieldy), so I transfer AST into a usual tree
def _ast_to_tree(node):
	if isinstance(node, ast.AST):
		root = Node(node)
		for kind, var in vars(node).items():
			if kind not in ('lineno', 'col_offset', 'ctx'):
				root.add_child(_ast_to_tree(var))
		return root
	elif isinstance(node, list):
		root = Node(node)
		for item in node:
			root.add_child(_ast_to_tree(item))
		return root
	else:
		pass"""