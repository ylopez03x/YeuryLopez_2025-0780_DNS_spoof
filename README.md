# DNS Spoofing - DNS Poisoning Attack
**Autor:** Yeury Lopez  
**Matrícula:** 2025-0780  
**Curso:** Networking Security  

---

## 📹 Video del Ataque
> [https://www.youtube.com/watch?v=H_yT_XI9EZE]

---

## 🎯 Objetivo del Laboratorio

Demostrar cómo un atacante puede comprometer la resolución DNS de una víctima, redirigiendo el tráfico del dominio `itla.edu.do` hacia un servidor web falso controlado por el atacante, sin que la víctima note ninguna diferencia aparente.

---

## 🎯 Objetivo del Script

El script `dns_spoof.py` actúa como un servidor DNS falso que escucha en el puerto 53. Cuando recibe una consulta para `itla.edu.do`, responde con la IP del atacante en lugar de la IP real, redirigiendo a la víctima hacia una página web falsa.

### Parámetros usados

| Parámetro | Valor | Descripción |
|---|---|---|
| `IFACE` | `eth0` | Interfaz de red del atacante |
| `FAKE_IP` | `172.20.25.100` | IP del servidor web falso (Kali) |
| `PORT` | `53` | Puerto DNS estándar |
| `SPOOF_DOMAINS` | `itla.edu.do` | Dominio a falsificar |
| `TTL` | `10` | Time to live de la respuesta falsa |

### Requisitos para utilizar la herramienta

```bash
# Sistema operativo
Kali Linux

# Dependencias
pip3 install scapy
sudo apt install apache2

# Permisos
sudo (root)

# Red
Kali y víctima en la misma red
Víctima configurada con Kali como servidor DNS
Puerto 53 UDP disponible en Kali
```

---

## 📋 Documentación del funcionamiento del script

El script opera como servidor DNS completo:

```
Ubuntu consulta: itla.edu.do → 172.20.25.100:53
                                      ↓
Script recibe la consulta UDP en puerto 53
Script verifica si el dominio está en SPOOF_DOMAINS
Script construye respuesta DNS con IP falsa 172.20.25.100
Script envía respuesta al cliente
                                      ↓
Ubuntu recibe: itla.edu.do = 172.20.25.100 (IP de Kali)
Ubuntu visita: http://itla.edu.do → Página web falsa de Kali
```

**Flujo detallado:**
1. Script inicia socket UDP en `0.0.0.0:53`
2. Espera consultas DNS entrantes
3. Por cada consulta recibida, lanza un thread
4. El thread parsea el paquete DNS con Scapy
5. Si el dominio coincide con `itla.edu.do`, construye respuesta falsa
6. Para otros dominios, responde con NXDOMAIN
7. Envía la respuesta al cliente

---

## 🌐 Documentación de la Red

### Topología

<img width="975" height="592" alt="image" src="https://github.com/user-attachments/assets/fb5c5cac-2219-44d9-adbf-1e7eb15f3b3a" />

```

### Direccionamiento IP

| Dispositivo | Interfaz | IP | Rol |
|---|---|---|---|
| Kali Linux | eth0 | 172.20.25.100/24 | Atacante / DNS falso / Web falso |
| Ubuntu | ens3 | 172.20.25.200/24 | Víctima |
| Router | fa0/0 | 172.20.25.1/24 | Gateway / DNS legítimo |

### VLANs

| VLAN ID | Nombre | Dispositivos |
|---|---|---|
| 10 | LAB | Kali, Ubuntu, Router (misma red) |

---
```

## 📸 Capturas de pantalla requeridas

### nslookup itla.edu.do desde Ubuntu con DNS real (8.8.8.8)
![nslookup dns real](https://github.com/user-attachments/assets/275ef7b8-24e7-4bf6-a471-8f56276a8870)

### systemctl status apache2 en Kali
![apache2 status](https://github.com/user-attachments/assets/f0c97258-6e8c-473e-bcf6-d06d1c6a4aff)

### Script dns_spoof.py iniciando en Kali
![dns spoof script](https://github.com/user-attachments/assets/6619ec4b-b50b-46d8-a04e-25cbfc1924b0)

### nslookup itla.edu.do mostrando IP falsa y curl pagina falsa
![dns spoofed y curl](https://github.com/user-attachments/assets/d14a2cae-d88f-4c98-87f6-a7863964f0f8)

### Configuracion DNS legitimo en el Router
![router dns contramedida](https://github.com/user-attachments/assets/0e3e8f65-756c-4f7c-972f-3c74d1eef396)


---

## 🛡️ Contramedidas

### Contramedida 1 — Configurar servidor DNS legítimo en el Router

```
R1# configure terminal
R1(config)# ip dns server
R1(config)# ip host itla.edu.do 192.168.1.1
R1(config)# ip domain-lookup
R1(config)# end
R1# write memory
```

En Ubuntu apuntar al router:
```bash
echo "nameserver 172.20.25.1" | sudo tee /etc/resolv.conf
```

**Por qué funciona:** Si la víctima usa un servidor DNS confiable (el router), el script de Kali no recibe ninguna consulta DNS y no puede falsificar respuestas.

### Contramedida 2 — Usar DNSSEC

```bash
# En Ubuntu verificar con DNSSEC
dig +dnssec itla.edu.do
```

**Por qué funciona:** DNSSEC firma criptográficamente las respuestas DNS. Si la firma no es válida, el cliente rechaza la respuesta, detectando el spoofing.

### Contramedida 3 — Usar DNS sobre HTTPS (DoH)

```bash
# Configurar DoH en Ubuntu
sudo apt install systemd-resolved
sudo nano /etc/systemd/resolved.conf
# Agregar:
# DNS=1.1.1.1
# DNSOverTLS=yes
sudo systemctl restart systemd-resolved
```

**Por qué funciona:** DNS sobre HTTPS cifra el tráfico DNS, haciendo imposible que un atacante en la misma red intercepte o falsifique las consultas.

### Contramedida 4 — Monitoreo de red

Detectar DNS Spoofing monitoreando respuestas DNS sospechosas:
```bash
# En cualquier host de la red
sudo tcpdump -i eth0 -nn udp port 53
```

Señales de alerta:
- Múltiples respuestas DNS para la misma consulta
- Respuestas DNS con TTL muy bajo (como el TTL=10 del script)
- Respuestas DNS de IPs no autorizadas

---

## 🔧 Cómo ejecutar

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/dns-spoofing

# 2. Instalar dependencias
pip3 install scapy
sudo apt install apache2

# 3. Iniciar Apache (servidor web falso)
sudo systemctl start apache2

# 4. Configurar la víctima para usar Kali como DNS
# En Ubuntu: echo "nameserver 172.20.25.100" | sudo tee /etc/resolv.conf

# 5. Ejecutar el script
sudo python3 dns_spoof.py
```

---

## ⚠️ Disclaimer

Este script es únicamente para fines educativos y de laboratorio. El uso de esta herramienta en redes sin autorización expresa es ilegal y está penado por la ley.
