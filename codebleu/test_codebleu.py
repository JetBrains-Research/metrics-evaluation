import unittest
import os
import codebleu_metric as cbl


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

    def test_parse_occurences(self):



if __name__ == '__main__':
    unittest.main()