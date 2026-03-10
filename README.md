# 🚀 P4-Based In-Network DDoS Mitigation

This project implements an **In-Network DDoS Mitigation system using the P4 language**. By leveraging the programmable **data plane of a BMv2 software switch**, the system detects and drops **high-rate TCP SYN flood attacks at line rate**.

Unlike traditional **SDN approaches** that forward suspicious traffic to a controller, this solution performs mitigation **directly inside the switch data plane**, enabling:

- ⚡ **Sub-millisecond response times**
- 🧠 **No controller dependency**
- 💻 **Zero CPU overhead during attacks**

---

# 💡 Key Features

### 🔹 Data Plane Enforcement
Packet inspection and dropping occur entirely within the **BMv2 programmable switch**.

### 🔹 Stateless Rate Limiting
Uses **P4 Meters (Two-Rate Three-Color Marker)** to track TCP SYN packet velocity.

### 🔹 Zero Controller Dependency
Mitigation logic runs completely inside the switch without requiring **ONOS, Ryu, or any SDN controller**.

### 🔹 Dockerized Environment
Fully portable setup using:

- **p4c compiler**
- **Mininet**
- **Scapy**
- **BMv2**

---

# 🛠 Prerequisites

Make sure the following tools are installed on your system:

- **Docker**
- **Docker Compose**

---

# 🚀 Getting Started

## 1️⃣ Provision the Environment

Build and launch the containerized **Ubuntu 20.04 environment** containing the P4 toolchain.

```bash
docker-compose up -d --build
docker exec -it p4_ddos_env /bin/bash
```

All subsequent commands should be executed **inside this container**.

---

## 2️⃣ Compilation

The P4 program is compiled automatically during the Docker build.

If you modify the file:

```
p4-src/ddos_mitigation.p4
```

Recompile using:

```bash
p4c-bm2-ss --p4v 16 -o /app/ddos_mitigation.json /app/p4-src/ddos_mitigation.p4
```

---

## 3️⃣ Launch Network Topology

Start the **Mininet topology (1 Switch, 2 Hosts)** and load the compiled P4 program into the BMv2 switch.

```bash
python3 /app/topology/network.py
```

You will now enter the **Mininet CLI**:

```
mininet>
```

---

# 🧪 Testing the Mitigation

## Scenario A: Normal Traffic (Baseline)

### Step 1: Monitor traffic on Host 2

```bash
mininet> h2 tcpdump -i h2-eth0 -n tcp &
```

### Step 2: Send low-rate traffic from Host 1

```bash
mininet> h1 python3 /app/scripts/send_normal_traffic.py 10.0.0.2
```

### Result

All **10 packets** successfully arrive at **Host 2 (h2)**.

---

# 🚨 Scenario B: SYN Flood Attack (Mitigation)

Launch a **high-rate TCP SYN flood attack** to trigger the P4 meter.

```bash
mininet> h1 python3 /app/scripts/send_syn_flood.py 10.0.0.2
```

### Observation

The switch detects the rate violation:

- Initial **GREEN packets** are allowed
- **RED packets** exceed the threshold
- RED packets are **immediately dropped in the switch**

This prevents the attack traffic from reaching the destination host.

---

### Cleanup

Stop packet monitoring:

```bash
mininet> h2 kill %tcpdump
```

---

# 🏗 System Architecture

The **P4 pipeline** follows these logical stages:

### 1️⃣ Parser
Extracts the following headers:

- Ethernet
- IPv4
- TCP

### 2️⃣ Ingress Match-Action

Checks if:

```
TCP.flags = SYN
AND
TCP.flags != ACK
```

If true:

- Apply a **Meter indexed by destination IP**

### 3️⃣ Meter Logic

The meter calculates **packet rate** and assigns a color state.

### 4️⃣ Drop Logic

If the packet is classified as **RED**, the following primitive is executed:

```
mark_to_drop()
```

This causes the packet to be dropped immediately.

---

# 📊 Meter Configuration

The mitigation uses a **color-aware implementation**.

| State | Action | Description |
|------|------|------|
| Green | NoAction | Traffic allowed |
| Yellow | NoAction | Optional throttling (currently allowed) |
| Red | drop() | Packet immediately dropped |

---

# 📂 Project Structure

```
.
├── p4-src/
│   └── ddos_mitigation.p4      # Core P4-16 source code
│
├── scripts/
│   ├── send_normal_traffic.py
│   └── send_syn_flood.py       # Scapy-based attack generator
│
├── topology/
│   └── network.py              # Mininet topology definition
│
├── Dockerfile                  # Container environment
├── docker-compose.yml          # Container orchestration
└── README.md
```

---

# ⚙️ Technologies Used

- **P4-16**
- **BMv2 Software Switch**
- **Mininet**
- **Scapy**
- **Docker**
- **Python**

---

# 📌 Future Improvements

Possible extensions of this project include:

- Adaptive thresholds using **machine learning**
- Multi-switch distributed mitigation
- Integration with **SDN controllers**
- Detection of additional attack types such as:
  - UDP floods
  - ICMP floods
  - Amplification attacks

---

# 📜 License

This project is open-source and available under the **MIT License**.

---

# 👨‍💻 Author

Developed as part of a **network security / programmable networks project** demonstrating **data-plane DDoS mitigation using P4**.
