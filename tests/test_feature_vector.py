import numpy as np
from ryu_app import feature_extractor

def test_feature_len():
    dummy = {
        'ip_src': '10.0.0.1',
        'ip_dst': '10.0.0.2',
        'ip_proto': 6,
        'tcp_sport': 12345,
        'tcp_dport': 23,
        'tcp_flags': 2,
        'pkt_len': 128,
        'payload_len': 108
    }
    v = feature_extractor.packet_to_feature_vector(dummy)
    assert v.shape[0] == len(feature_extractor.FEATURE_NAMES)
    print("Feature vector length:", v.shape[0])
    print("First 8 values:", v[:8])

if __name__ == "__main__":
    test_feature_len()
