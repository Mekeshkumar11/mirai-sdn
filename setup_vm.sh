#!/bin/bash
set -e
echo "==> updating apt"
sudo apt update

echo "==> install common tools"
sudo apt install -y git build-essential python3-pip python3-dev openvswitch-switch \
    openvswitch-common openvswitch-controller tcpdump wget iperf3 hping3

echo "==> install Mininet (if not installed)"
sudo apt install -y mininet

echo "==> install Ryu via pip"
pip3 install ryu==5.4.0

echo "==> install python packages"
pip3 install -r requirements.txt

echo "==> done. Note: run ryu-manager as root or with permissions to access OVS."
