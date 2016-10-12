import unittest
import os

from utils.kubernetes import KubeStateProcessor
from utils.prometheus import parse_metric_family

import mock


class TestKubeStateProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Preload all protobuf messages in a dict so we can use during
        unit tests without cycling every time the binary buffer.
        """
        cls.messages = {}
        f_name = os.path.join(os.path.dirname(__file__), 'fixtures', 'prometheus', 'protobuf.bin')
        with open(f_name, 'rb') as f:
            for msg in parse_metric_family(f.read()):
                cls.messages[msg.name] = msg

    def setUp(self):
        self.check = mock.MagicMock()
        self.processor = KubeStateProcessor(self.check)

    def test_process(self):
        metric = mock.MagicMock()
        metric.name = 'foo'
        self.processor.process(metric)  # this should never fail

        metric.name = 'a_metric'
        method = mock.MagicMock()
        setattr(self.processor, 'a_metric', method)
        self.processor.process(metric)
        method.assert_called_once()

    def test_kube_node_status_capacity_cpu_cores(self):
        msg = self.messages['kube_node_status_capacity_cpu_cores']
        self.processor.kube_node_status_capacity_cpu_cores(msg)

        expected = [
            ('kubernetes.node.cpu_capacity', 1.0, ['host:gke-cluster-massi-agent59-default-pool-6087cc76-9cfa']),
            ('kubernetes.node.cpu_capacity', 1.0, ['host:gke-cluster-massi-agent59-default-pool-6087cc76-aah4']),
            ('kubernetes.node.cpu_capacity', 1.0, ['host:gke-cluster-massi-agent59-default-pool-6087cc76-fgnk']),
        ]

        calls = self.check.publish_gauge.mock_calls
        self.assertEqual(len(calls), 3)
        for i, call in enumerate(calls):
            args = call[1]
            self.assertEqual(args[1:], expected[i])  # skip the first call arg, it's the `self`
