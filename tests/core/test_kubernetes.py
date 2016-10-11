import unittest
import os

from utils.kubernetes import KubeStateProcessor

import mock


class TestKubeStateProcessor(unittest.TestCase):
    def setUp(self):
        self.check = mock.MagicMock()
        self.processor = KubeStateProcessor(self.check)

    def test_process(self):
        metric = mock.MagicMock()
        metric.name = 'foo'
        self.processor.process(metric)  # this should never fail

        method = mock.MagicMock()
        metric.name = 'a_metric'
        setattr(self.processor, 'a_metric', method)
        self.processor.process(metric)
        method.assert_called_once()

    def test__update_kube_state_metrics(self):
        # TODO check the mocked check to see if gauges et al were called properly
        f_name = os.path.join(os.path.dirname(__file__), 'fixtures', 'prometheus', 'protobuf.bin')
        with open(f_name, 'rb') as f:
            self.check._get_kube_state = mock.MagicMock()
            self.check._get_kube_state.return_value = f.read()
            self.check._update_kube_state_metrics()
