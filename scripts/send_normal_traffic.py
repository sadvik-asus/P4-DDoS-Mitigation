import argparse
import sys
import socket
import random
import struct
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
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
    parser.add_argument('ip_addr', type=str, help="The destination IP address")
    parser.add_argument('--count', type=int, default=10, help="Number of packets to send")
    parser.add_argument('--interval', type=float, default=0.5, help="Interval between packets")
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    
    for i in range(args.count):
        # Sending normal TCP traffic (e.g., HTTP request)
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff') / \
              IP(dst=addr) / \
              TCP(dport=80, sport=random.randint(1024, 65535), flags='S')
        
        # Adding a sequence number or payload just to distinguish normal traffic easily
        pkt = pkt / "Normal Traffic Payload"
        
        pkt.show()
        sendp(pkt, iface=iface, verbose=False)
        # Using a slow interval to not trigger the rate limiter
        sys.stdout.flush()
        import time
        time.sleep(args.interval)

if __name__ == '__main__':
    main()
