# deep_packet_inspection.py
from scapy.all import sniff, IP, TCP, UDP

def inspect_packet(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        protocol = packet[IP].proto

        print("=" * 60)
        print(f"Source IP      : {src_ip}")
        print(f"Destination IP : {dst_ip}")
        print(f"Protocol       : {protocol}")

        if TCP in packet:
            print(f"TCP Port       : {packet[TCP].sport} -> {packet[TCP].dport}")

        elif UDP in packet:
            print(f"UDP Port       : {packet[UDP].sport} -> {packet[UDP].dport}")

        print(f"Packet Size    : {len(packet)} bytes")

def main():
    print("[+] Starting packet inspection...")
    sniff(prn=inspect_packet, store=False)

if __name__ == "__main__":
    main()