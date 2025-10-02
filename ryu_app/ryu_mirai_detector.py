from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp
from ryu.ofproto import ofproto_v1_3

import time
import os
import logging
import numpy as np

from ryu_app import feature_extractor, preprocessing, tf_model, prevention
import yaml

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(BASE_DIR, 'configs', 'model_config.yaml')
with open(CONFIG_PATH) as f:
    CFG = yaml.safe_load(f)

THRESHOLD = float(CFG.get('threshold', 0.7))
ATTACK_IDX = int(CFG.get('attack_index', 1))
FEATURE_COUNT = int(CFG.get('input_shape', {}).get('features', 48))

LOG = logging.getLogger('ryu.app.mirai_detector')

class MiraiDetector(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MiraiDetector, self).__init__(*args, **kwargs)
        LOG.setLevel(logging.INFO)
        LOG.info("MiraiDetector starting up")
        # lazy load model (tf_model loads on first call)
        try:
            _ = tf_model.load_tf_model()
            LOG.info("TensorFlow model loaded")
        except Exception as e:
            LOG.error("Failed to load TensorFlow model at startup: %s", e)
        LOG.info("Threshold=%s attack_index=%s", THRESHOLD, ATTACK_IDX)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match.get('in_port', None)
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if ip_pkt is None:
            return  # only process IPv4
        src = ip_pkt.src
        dst = ip_pkt.dst
        proto = ip_pkt.proto
        pkt_len = len(msg.data)
        # gather basic fields
        parsed = {
            'ip_src': src,
            'ip_dst': dst,
            'ip_proto': proto,
            'pkt_len': pkt_len,
            'payload_len': pkt_len - 20  # rough; you can refine
        }
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        if tcp_pkt:
            parsed.update({
                'tcp_sport': getattr(tcp_pkt, 'src_port', getattr(tcp_pkt, 'src', 0)),
                'tcp_dport': getattr(tcp_pkt, 'dst_port', getattr(tcp_pkt, 'dst', 0)),
                'tcp_flags': getattr(tcp_pkt, 'bits', 0)
            })
        if udp_pkt:
            parsed.update({
                'udp_sport': getattr(udp_pkt, 'src_port', getattr(udp_pkt, 'src', 0)),
                'udp_dport': getattr(udp_pkt, 'dst_port', getattr(udp_pkt, 'dst', 0)),
            })
        # build feature vector (single-row)
        try:
            vec = feature_extractor.packet_to_feature_vector(parsed)
        except Exception as e:
            LOG.exception("feature_extractor failed: %s", e)
            return
        if vec.size != FEATURE_COUNT:
            LOG.warning("feature vector length mismatch: expected %d got %d", FEATURE_COUNT, vec.size)
        # preprocess
        vec_p = preprocessing.preprocess_vector(vec)
        # inference
        try:
            probs = tf_model.predict_proba(vec_p)
        except Exception as e:
            LOG.exception("Model inference failed: %s", e)
            return
        attack_prob = float(probs[ATTACK_IDX]) if probs.size > ATTACK_IDX else float(probs.max())
        LOG.info("Packet from %s -> attack_prob=%.4f", src, attack_prob)
        if attack_prob >= THRESHOLD:
            LOG.warning("Attack detected from %s (prob=%.3f). Blocking...", src, attack_prob)
            prevention.block_ip(datapath, src, idle_timeout=60)
            # optionally, log to file
            try:
                with open(os.path.join(BASE_DIR, 'data', 'logs', 'detections.log'), 'a') as fh:
                    fh.write(f"{time.time()},{src},{attack_prob}\n")
            except Exception:
                pass
