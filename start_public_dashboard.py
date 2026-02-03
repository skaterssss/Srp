#!/usr/bin/env python3
"""
Start dashboard with public access (no password required)
Uses Serveo SSH tunnel or shows instructions for cloud port forwarding
"""

import subprocess
import time
import sys
import socket

def check_port(port):
    """Check if port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def get_public_ip():
    """Try to get public IP"""
    try:
        import requests
        return requests.get('https://api.ipify.org', timeout=3).text
    except:
        return None

print("🌾 Starting Agri-Market Dashboard with Public Access\n")

# Check if Flask is running
if not check_port(5000):
    print("⚠️  Dashboard not running on port 5000")
    print("Starting Flask dashboard...")
    subprocess.Popen([
        'python3', '-m', 'flask', 
        '--app', 'dashboard/app', 
        'run', 
        '--host=0.0.0.0', 
        '--port=5000'
    ])
    print("✅ Dashboard started on http://localhost:5000\n")
    time.sleep(3)
else:
    print("✅ Dashboard already running on port 5000\n")

print("="*60)
print("📱 MOBILE ACCESS OPTIONS")
print("="*60)

# Option 1: Check if we're in a cloud environment
print("\n🌐 OPTION 1: Port Forwarding (BESTE - GEEN PASSWORD!)")
print("-"*60)
print("Als je in VS Code / Cursor / GitHub Codespaces zit:")
print("  1. Kijk naar de 'PORTS' tab onderaan je editor")
print("  2. Poort 5000 zou zichtbaar moeten zijn")
print("  3. Klik op het 🌐 globe icoon voor publieke URL")
print("  4. Die URL werkt direct op mobile - GEEN PASSWORD!")
print()
print("Voorbeeld URL: https://[workspace-id]-5000.app.github.dev")

# Option 2: SSH tunnel via Serveo
print("\n🔧 OPTION 2: Serveo SSH Tunnel (Gratis, geen account)")
print("-"*60)
print("Voer dit commando uit in een nieuwe terminal:")
print()
print("  ssh -R 80:localhost:5000 serveo.net")
print()
print("Je krijgt dan een URL zoals: https://abc123.serveo.net")
print("Deze werkt DIRECT zonder password!")

# Option 3: Bore tunnel
print("\n🚀 OPTION 3: Bore Tunnel (Simpel)")
print("-"*60)
print("Installeer bore:")
print("  cargo install bore-cli")
print("  # Of download van: https://github.com/ekzhang/bore")
print()
print("Start tunnel:")
print("  bore local 5000 --to bore.pub")

# Option 4: Cloudflare tunnel
print("\n☁️  OPTION 4: Cloudflare Tunnel (Pro)")
print("-"*60)
print("Voor permanente, veilige hosting:")
print("  1. Installeer: wget -O cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb")
print("  2. sudo dpkg -i cloudflared.deb")
print("  3. cloudflared tunnel --url http://localhost:5000")
print()
print("Geen account nodig voor quick links!")

print("\n" + "="*60)
print("💡 SIMPELSTE OPLOSSING")
print("="*60)
print("Gebruik OPTION 1 (Port Forwarding) als je in een cloud IDE zit.")
print("Anders: gebruik OPTION 2 (Serveo) - werkt altijd!\n")

# Try Serveo automatically
print("\n🔄 Starting Serveo tunnel automatically...\n")
print("Copy this command to start the tunnel:")
print()
print("  ssh -R 80:localhost:5000 serveo.net")
print()
print("Press CTRL+C to cancel and use a different option\n")

try:
    # Start serveo
    proc = subprocess.Popen(
        ['ssh', '-R', '80:localhost:5000', 'serveo.net'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print("Connecting to Serveo...")
    for i, line in enumerate(proc.stdout):
        print(line.rstrip())
        if 'Forwarding HTTP traffic from' in line or 'https://' in line:
            print("\n" + "="*60)
            print("✅ TUNNEL ACTIEF!")
            print("="*60)
            break
        if i > 20:  # Safety limit
            break
    
    print("\n🎉 Dashboard is now publicly accessible!")
    print("Keep this terminal open to maintain the connection.\n")
    
    # Keep running
    proc.wait()
    
except KeyboardInterrupt:
    print("\n\n⚠️  Tunnel stopped. Dashboard still running locally.")
    print("Use one of the options above to create public access.\n")
except Exception as e:
    print(f"\n⚠️  Serveo failed: {e}")
    print("\nTry one of the other options above!")

print("\n" + "="*60)
print("Dashboard remains running on http://localhost:5000")
print("="*60)
