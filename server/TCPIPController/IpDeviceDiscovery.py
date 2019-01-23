import subprocess
import re


def find_network_devices(debug=False):
    response = subprocess.run(['nmap', '-sn', '10.161.35.1/24'], stdout=subprocess.PIPE)
    devices = response.stdout.decode('utf-8')
    devicesSplit = devices.split('\n')

    if debug:
        for ip in ip_addresses:
            print(ip)
    ip_addresses = re.findall('([A-Z0-9]{2}:.*[A-Z0-9]{2}).*\n.*\s([a-zA-Z0-9\-]*).lan\s.*(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', devices)
    return ip_addresses
