#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def simple_topology():
    setLogLevel('info')
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSSwitch)
    info('*** Adding controller\n')
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')  # attacker
    h2 = net.addHost('h2', ip='10.0.0.2/24')  # victim
    h3 = net.addHost('h3', ip='10.0.0.3/24')  # honeypot
    s1 = net.addSwitch('s1')
    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    info('*** Starting network\n')
    net.start()
    info('*** Running CLI\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    simple_topology()
