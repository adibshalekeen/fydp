import subprocess
import re


response = subprocess.run(['nmap', '-sn', '10.161.35.1/24'], stdout=subprocess.PIPE)
devices = response.stdout.decode('utf-8')
devicesSplit = devices.split('\n')

for line in devicesSplit:
    if "Nmap scan report" in line or "MAC Address" in line:
        print(line)

ip_addresses = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', devices)
for ip in ip_addresses:
    print(ip)
