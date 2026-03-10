# P4-Based In-Network DDoS Mitigation

This project demonstrates a Software-Defined Networking (SDN) data plane approach to network security. It uses a P4 program running on a BMv2 software switch to automatically detect and drop high-rate TCP SYN flood attacks without relying on an external CPU controller for the per-packet logic.

## Requirements
* Docker
* Docker Compose

The environment relies on a Linux container (Ubuntu 20.04) installing the necessary `p4lang` tools, Mininet, and Scapy. This makes it easy to run on Windows via Docker Desktop.

## Setup and Execution

### 1. Start the Environment
Use Docker Compose to build and start the container:
```bash
docker-compose up -d --build
```

Then, attach to the running container's shell:
```bash
docker exec -it p4_ddos_env /bin/bash
```

*Note: You will run the rest of the commands from inside the container.*

### 2. Compile the P4 Program (Optional)
The Dockerfile compiles the P4 program automatically during the build process. If you make modifications to `p4-src/ddos_mitigation.p4`, recompile it with:
```bash
p4c-bm2-ss --p4v 16 -o /app/ddos_mitigation.json /app/p4-src/ddos_mitigation.p4
```

### 3. Start the Mininet Topology
Run the Mininet script which will start the BMv2 switch and two hosts (`h1` and `h2`), and will populate the routing tables automatically:
```bash
python3 /app/topology/network.py
```
This will open the `mininet>` prompt.

### 4. Testing Normal Traffic
At the mininet prompt, let's observe traffic on `h2`:
```bash
mininet> h2 tcpdump -i h2-eth0 -n tcp &
```

Now, send normal traffic from `h1` to `h2` (10 packets with half-second intervals):
```bash
mininet> h1 python3 /app/scripts/send_normal_traffic.py 10.0.0.2
```
You should see all 10 packets successfully arrive at `h2`.
Stop the tcpdump with:
```bash
mininet> h2 kill %tcpdump
```

### 5. Testing SYN Flood Mitigation
The P4 switch is configured with a meter to track SYN packet rates. If a flood occurs, the data plane will mark the excessive packets to be dropped.

Run tcpdump on `h2` again:
```bash
mininet> h2 tcpdump -i h2-eth0 -n tcp &
```

Now, launch a rapid SYN flood from `h1` to `h2` (1000 packets at line rate):
```bash
mininet> h1 python3 /app/scripts/send_syn_flood.py 10.0.0.2
```
You will notice `h2` receives only a handful of the initial packets (until the rate meter turns from GREEN to YELLOW/RED state), and the rest are dropped entirely in the data plane by the P4 switch before they reach the victim host!

Stop the tcpdump with:
```bash
mininet> h2 kill %tcpdump
```

## How It Works
1. **Parser**: The `ddos_mitigation.p4` defines standard headers (Ethernet, IPv4, TCP).
2. **Meter**: An Ingress meter tracks the volume of traffic (specifically TCP SYN packets).
3. **Logic**: When parsing a packet, if it's a TCP SYN (and not an ACK), it updates the meter corresponding to the target destination IP.
4. **Action**: If the meter threshold is exceeded, the switch executes the `drop()` action, effectively mitigating volumetric resource enumeration without CPU intervention.
