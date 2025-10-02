#!/usr/bin/env python3
from scapy.all import IP, TCP, send
import time

TARGET = "10.0.0.2"   # victim
ports = [23, 2323, 80] + list(range(200, 210))  # example mix

print(f"Starting scan from attacker to {TARGET}")
for p in ports:
    pkt = IP(dst=TARGET)/TCP(dport=p, flags='S')
    send(pkt, verbose=False)
    time.sleep(0.01)
print("Scan finished.")
