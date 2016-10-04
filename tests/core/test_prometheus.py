import unittest
import os

from utils.prometheus import parse_metric_family


class TestPrometheusFuncs(unittest.TestCase):
    def test_parse_metric_family(self):
        f_name = os.path.join(os.path.dirname(__file__), 'fixtures', 'prometheus', 'protobuf.bin')
        with open(f_name, 'rb') as f:
            data = f.read()
            self.assertEqual(len(data), 38347)
            messages = list(parse_metric_family(data))
            self.assertEqual(len(messages), 56)
            self.assertEqual(messages[-1].name, 'process_virtual_memory_bytes')
