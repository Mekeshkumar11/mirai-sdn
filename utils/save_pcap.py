from scapy.all import wrpcap, PacketList
import os
import time

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'pcap'))
os.makedirs(OUT_DIR, exist_ok=True)

def save_packets(pkt_list, name=None):
    if not pkt_list:
        return None
    ts = int(time.time())
    if not name:
        name = f"capture_{ts}.pcap"
    out = os.path.join(OUT_DIR, name)
    wrpcap(out, PacketList(pkt_list))
    return out
