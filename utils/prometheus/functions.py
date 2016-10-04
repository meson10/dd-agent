from google.protobuf.internal.decoder import _DecodeVarint32  # pylint: disable=E0611,E0401

from . import metrics_pdb2


def parse_metric_family(buf):
    n = 0
    while n < len(buf):
        msg_len, new_pos = _DecodeVarint32(buf, n)
        n = new_pos
        msg_buf = buf[n:n+msg_len]
        n += msg_len

        message = metrics_pdb2.MetricFamily()
        message.ParseFromString(msg_buf)
        yield message
