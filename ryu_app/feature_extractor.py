import yaml
import os
import numpy as np
from ryu.lib.packet import ether_types

# load feature map
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FEATURE_MAP_PATH = os.path.join(BASE_DIR, 'configs', 'feature_map.yaml')

with open(FEATURE_MAP_PATH) as f:
    cfg = yaml.safe_load(f)
FEATURE_NAMES = cfg.get('features', [])
FEATURE_COUNT = len(FEATURE_NAMES)

def empty_vector():
    return np.zeros(FEATURE_COUNT, dtype=np.float32)

def packet_to_feature_vector(pkt_parsed):
    """
    pkt_parsed: an object with attributes extracted from Ryu packet parsing:
        a dictionary-like with keys we attempt to use:
        - ip_src, ip_dst, ip_proto, tcp_sport, tcp_dport, tcp_flags, udp_sport, udp_dport, pkt_len
    Return: numpy array shape (FEATURE_COUNT,)
    """
    vec = empty_vector()
    # create a simple mapping from common names to values
    m = {
        'ip_src': pkt_parsed.get('ip_src', ''),
        'ip_dst': pkt_parsed.get('ip_dst', ''),
        'ip_proto': float(pkt_parsed.get('ip_proto', 0)),
        'tcp_sport': float(pkt_parsed.get('tcp_sport', 0)),
        'tcp_dport': float(pkt_parsed.get('tcp_dport', 0)),
        'tcp_flags': float(pkt_parsed.get('tcp_flags', 0)),
        'udp_sport': float(pkt_parsed.get('udp_sport', 0)),
        'udp_dport': float(pkt_parsed.get('udp_dport', 0)),
        'pkt_len': float(pkt_parsed.get('pkt_len', 0)),
        'payload_len': float(pkt_parsed.get('payload_len', 0)),
        # add other raw fields/derived as you like
    }

    # Very important: You must map your exact 48 features here when you share them.
    # For now, if the feature name is in m, use it; else leave 0 (or implement custom derivations).
    for i, fname in enumerate(FEATURE_NAMES):
        if fname in m:
            try:
                vec[i] = float(m[fname])
            except Exception:
                vec[i] = 0.0
        else:
            # If the feature name is like "is_tcp" or "dst_port_23", handle some heuristics:
            if fname.startswith('is_tcp'):
                vec[i] = 1.0 if m.get('ip_proto',0) == 6 else 0.0
            elif fname.startswith('is_udp'):
                vec[i] = 1.0 if m.get('ip_proto',0) == 17 else 0.0
            else:
                vec[i] = 0.0
    return vec
