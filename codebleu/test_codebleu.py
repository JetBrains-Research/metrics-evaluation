import unittest
import collections
import codebleu_metric as cbl
import codebleu.graph_generator.graphgenerator as gg
import networkx as nx
from graph_generator.graphgenerator import AstGraphGenerator
from graph_generator.graphgenutils import prettyprint_graph
from graph_generator.type_lattice_generator import TypeLatticeGenerator


class TestGraphGenerator(unittest.TestCase):
    lattice = TypeLatticeGenerator('codebleu/typingRules.json')

    def test_inlist(self):
        self.assertEqual(cbl._inlist(1, [1, 2, 3]), True)
        self.assertEqual(cbl._inlist(1, [5, 2, 3]), False)
        self.assertEqual(cbl._inlist(1, 1), True)
        self.assertEqual(cbl._inlist(1, 2), False)

    def test_split_identifier(self):
        self.assertEqual(cbl._split_identifier('1_asd'), [1, 'asd'])
        self.assertEqual(cbl._split_identifier('1_asd_e'), [1, 'asd_e'])
        self.assertRaises(Exception, cbl._split_identifier('1_'))
        self.assertRaises(Exception, cbl._split_identifier('123'))
        self.assertRaises(Exception, cbl._split_identifier('asd_a'))
        self.assertRaises(Exception, cbl._split_identifier('___'))
        self.assertRaises(Exception, cbl._split_identifier('_asd'))

    def test_fix_graph(self):
        # not sure how to test properly here
        test_1 = gg.AstGraphGenerator('i=2\ni = i + 1', type_graph=self.lattice).build()
        test_1_dic = cbl._fix_graph(test_1)
        self.assertEqual(test_1_dic['edges']['NEXT_USE'], {'3_i': ['14_i'], '14_i': ['10_i']})
        self.assertEqual(test_1_dic['edges']['OCCURRENCE_OF'], {'3_i': ['4_i'], '10_i': ['4_i'], '14_i': ['4_i']})

    @staticmethod
    def _split_merge_identifier(myvar):
        split_myvar = cbl._split_identifier(myvar)
        update_myvar = str(split_myvar[0] - 1) + '_' + split_myvar[1]
        return update_myvar

    def test_parse_occurrences(self, g=None):
        if g is None:
            snp = gg.AstGraphGenerator('i=2\ni = i + 1', type_graph=self.lattice).build()
            g = cbl._fix_graph(snp)['edges']['OCCURRENCE_OF']
        ref_keys_list = []
        for val in list(g.values()):
            for item in val:
                ref_keys_list.append(self._split_merge_identifier(item))
        ref_keys = set(ref_keys_list)
        check_keys = set(cbl._parse_occurrences(g).keys())
        self.assertEqual(ref_keys, check_keys)

    def test_find_node(self, G=None, ids = None):
        if G is None:
            G = nx.DiGraph()
            ids = [i for i in range(1, 4)]
            for i in range(1, 4):
                G.add_node(i, id = i)
        for id in ids:
            self.assertEqual(cbl._find_node(G, id), id, msg=str(id))
        max_id = max(ids)
        self.assertIsNone(cbl._find_node(G, max_id + 2))
        self.assertIsNone(cbl._find_node(G, -1))

    def test_find_edge(self):
        G = nx.DiGraph()
        for i in range(1, 4):
            G.add_node(i, data=i)
        G.add_edge(1, 2)
        G.add_edge(1, 3)
        self.assertEqual(cbl._find_edge(G, (1,2)), (1,2))
        self.assertEqual(cbl._find_edge(G, (1, 3)), (1, 3))
        self.assertIsNone(cbl._find_edge(G, (2, 1)))
        self.assertIsNone(cbl._find_edge(G, (2, 3)))
        self.assertIsNone(cbl._find_edge(G, (15, 3)))

    def test_find_matching_variable(self, g = None):
        if g is None:
            g = {"51_i": 'a', '5_i': 'a', '22_j': 'b', '66_j': 'b'}
        self.assertEqual(cbl._find_matching_variable(g, '2_i')[1], '0_')
        self.assertEqual(cbl._find_matching_variable(g, '20_j'), [20, '0_'])
        self.assertEqual(cbl._find_matching_variable(g, '20_i'), [20, '5_i'])
        self.assertEqual(cbl._find_matching_variable(g, '60_i'), [60, '51_i'])
        self.assertEqual(cbl._find_matching_variable(g, '66_j'), [66, '66_j'])
        self.assertEqual(cbl._find_matching_variable(g, '66_t'), [66, '0_'])

    def test_compare_graphs(self):
        G = nx.DiGraph()
        G_node_shift = nx.DiGraph()
        G_data_shift = nx.DiGraph()
        for i in range(1, 4):
            G.add_node(i, data=i)
            G_node_shift.add_node(i+1, data=i)
            G_data_shift.add_node(i, data=i + 1)
        G.add_edges_from([(1, 2), (2, 3)])
        G_data_shift.add_edges_from([(1, 2), (2, 3)])
        G_node_shift.add_edges_from([(3, 4), (2, 3)])
        self.assertEqual(cbl._compare_graphs(G_data_shift, G), 1)
        self.assertEqual(cbl._compare_graphs(G_node_shift, G), 2)

    def test_create_graph(self):
        occurrence_dict = {'3_i': ['4_i'], '10_i': ['4_i'], '14_i': ['4_i']}
        next_use_dict = {'3_i': ['14_i'], '14_i': ['10_i']}
        var_dict = {'3_i': 'var_0'}
        G = cbl._create_graph(next_use_dict, var_dict, occurrence_dict)
        self.assertEqual(list(G.edges), [(0, 2), (2, 1)])
        self.assertEqual(len(G.nodes), 3)
        self.assertEqual(G.nodes[1]['data'], 'var_0')
        self.assertEqual(G.nodes[0]['id'], 3)

    def test_codebleu(self):
        self.assertEqual(cbl.codebleu("[1,2,3].sort()", "[1,2,3].sort()"), 1.0)


if __name__ == '__main__':
    unittest.main()
