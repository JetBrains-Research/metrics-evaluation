import json
import unittest
import collections

from codebleu.graph_generator.type_lattice_generator import TypeLatticeGenerator
from codebleu.bleu_score import compute_bleu as bleu
from codebleu.codebleu_metric import tokenize_builtin
import ruby.nx_graphs as nx_graphs
import ruby.util as util
from ruby.similarity import *
import networkx as nx
from tree_sitter import Language, Parser


class TestRubyMetric(unittest.TestCase):
    lattice = TypeLatticeGenerator('./codebleu/typingRules.json')

    def test_create_asts_and_graphs(self):
        nonempty_lines = ('a.sort(', 'x = "as', "def a():\nreturn 1", "def a()\n    return 1", "def a:\n    return 1")
        for line in nonempty_lines:
            # Not sure how to test here properly. I can't really compute AST or DFG in the required format
            # on a piece of paper, and I don't know, how to get them in another way
            self.assertIsNone(util.create_ast(line))
            self.assertIsNone(util.create_graph(line))
        nonempty_lines = ('a.sort()', 'list(1, 2, 3)', 'def a():\n    return 1', 'print("asd")')
        for line in nonempty_lines:
            self.assertIsNotNone(util.create_graph(line))
            self.assertIsNotNone(util.create_ast(line))

    # def test_get_ast_children(self):
    # the output here is a strange AST object that I'm not sure how to test


    def test_compute_ged(self):
        g = nx.DiGraph()
        h = nx.DiGraph()
        gp = nx.DiGraph()
        empty = nx.DiGraph()
        g.add_nodes_from([(i, {'label': i}) for i in range(3)])
        h.add_nodes_from([(i, {'label': i+1}) for i in range(3)])
        gp.add_nodes_from([(i+1, {'label': i}) for i in range(3)])
        for i in range(3):
            for j in range(i+1, 3):
                g.add_edge(i, j, label = 'a')
                h.add_edge(i, j,  label = 'b')
                gp.add_edge(i+1, j+1,  label = 'a')
        self.assertEqual(compute_ged(g, empty)[0], 3.0)
        self.assertEqual(compute_ged(g, empty, use_edge_cost=True)[0], 6.0)
        print(g.nodes.data())
        print(g.edges.data())
        print(h.nodes.data())
        print(h.edges.data())
        self.assertEqual(compute_ged(g, h)[0], 1.0)
        self.assertEqual(compute_ged(g, h, use_edge_cost=True)[0], 4.0)
        self.assertEqual(compute_ged(g, gp)[0], 0.0)
        self.assertEqual(compute_ged(g, gp, use_edge_cost=True)[0], 0.0)

    def compute_on_dataset(self, data, fields):
        for item in data:
            for field in fields:
                can = item[field]
                ref = item['snippet']
                if bleu([[tokenize_builtin(ref)]], [tokenize_builtin(can)])[0] == 1.0:
                    try:
                        self.assertEqual(tree_similarity(ref, can), 1.0)
                        self.assertEqual(graph_similarity(ref, can), 1.0)
                        self.assertEqual(string_similarity(ref, can), 1.0)
                    except AssertionError:
                        print(ref)
                        print(can)
                        raise AssertionError


    def test_on_dataset(self):
        conala_fields = ['baseline', 'tranx-annot', 'best-tranx', 'best-tranx-rerank']
        hs_fields = ['nl2code', 'gcnn']
        data_conala = json.load(open('./to-grade/all-singles.json'))[:-1]
        data_hearth = json.load(open('./to-grade/hs.json'))[:-1]
        self.compute_on_dataset(data_conala, conala_fields)
        self.compute_on_dataset(data_hearth, hs_fields)



if __name__ == '__main__':
    unittest.main()
