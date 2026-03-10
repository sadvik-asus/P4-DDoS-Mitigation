import os
import time
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Host, Switch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import subprocess

class P4Switch(Switch):
    """Custom Switch class for BMv2 simple_switch"""
    def __init__(self, name, json_path=None, **kwargs):
        Switch.__init__(self, name, **kwargs)
        self.json_path = json_path
        self.logfile = '/tmp/p4s.{}.log'.format(self.name)

    def start(self, controllers):
        info("Starting P4 switch {self.name}\n")
        args = ['simple_switch']
        args.extend(['--log-console'])
        args.extend(['-i', '1@s1-eth1', '-i', '2@s1-eth2']) # Hardcoding interfaces for simplicity
        if self.json_path:
            args.extend([self.json_path])
        else:
            info("WARNING: No JSON file provided for P4 switch %s\n" % self.name)
            
        args.append('--no-p4')  # Ignore P4 config initially if we wanted to push it via CLI, but since we are compiling it we can provide it.
        # Actually it's better to provide the compiled JSON directly
        
        args = ['simple_switch', '-i', '1@s1-eth1', '-i', '2@s1-eth2', self.json_path]
        
        cmd = ' '.join(args) + ' > ' + self.logfile + ' 2>&1 &'
        
        info(cmd + "\n")
        self.cmd(cmd)

    def stop(self):
        info("Stopping P4 switch {self.name}\n")
        self.cmd('kill %simple_switch')
        Switch.stop(self)

class SingleSwitchTopo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        s1 = self.addSwitch('s1', cls=P4Switch, json_path='/app/ddos_mitigation.json')
        
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

        self.addLink(h1, s1, port1=0, port2=1)
        self.addLink(h2, s1, port1=0, port2=2)

def main():
    topo = SingleSwitchTopo()
    net = Mininet(topo=topo, host=Host, controller=None)
    
    net.start()
    
    # We need to configure the switch via its CLI to add the routing rules
    # because the switch doesn't know where to forward out of the box.
    time.sleep(2) # Give the switch time to start
    
    info("\n*** Configuring P4 Switch Rules ***\n")
    # For a real implementation, you'd use the thrift API or `simple_switch_CLI`
    # Here we are calling simple_switch_CLI directly to populate the ipv4_lpm table.
    
    commands = [
        "table_add ipv4_lpm ipv4_forward 10.0.0.1/32 => 00:00:00:00:00:01 1",
        "table_add ipv4_lpm ipv4_forward 10.0.0.2/32 => 00:00:00:00:00:02 2"
    ]
    
    with open('/tmp/commands.txt', 'w') as f:
        f.write("\n".join(commands) + "\n")
        
    subprocess.call('simple_switch_CLI < /tmp/commands.txt', shell=True)
    
    # Also we need to disable offloading on the host interfaces for things to work well with Scapy and BMv2
    for host in net.hosts:
        host.cmd('ethtool --offload %s-eth0 rx off tx off sg off tso off' % host.name)
        # Add static ARPs so they don't depend on ARP logic in the P4 switch (which we omitted for simplicity)
        if host.name == 'h1':
            host.cmd('arp -i h1-eth0 -s 10.0.0.2 00:00:00:00:00:02')
        elif host.name == 'h2':
            host.cmd('arp -i h2-eth0 -s 10.0.0.1 00:00:00:00:00:01')
            
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
