import subprocess
import re
import os


def find_network_devices(debug=False):
    if os.name == "nt":
        ipconfigResp = subprocess.run(['ipconfig'], stdout=subprocess.PIPE)
        ipconfigResp = ipconfigResp.stdout.decode('utf-8')
        userIpAddress = re.findall('\s{3}IPv4\sAddress.*(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ipconfigResp)
        userIpAddress = userIpAddress[0] + "/24"
    elif os.name == "posix":
        ipconfigResp = subprocess.run(['ifconfig', 'wlan0'], stdout=subprocess.PIPE)
        ipconfigResp = ipconfigResp.stdout.decode('utf-8')
        userIpAddress = re.findall('inet\s(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ipconfigResp)
        userIpAddress = userIpAddress[0] + "/24"

    processToRun = ['sudo', 'nmap', '-sn', userIpAddress] if os.name == "posix" else ['nmap', '-sn', userIpAddress]
    print("Running command \'%s\'" % processToRun)
    response = subprocess.run(processToRun, stdout=subprocess.PIPE)
    devices = response.stdout.decode('utf-8')

    if debug:
        for ip in ip_addresses:
            print(ip)
    ip_addresses = re.findall('([A-Z0-9]{2}:.*[A-Z0-9]{2})\s\(([A-Za-z0-9\s]*)\).*\n.*\s([a-zA-Z0-9\-.]*)\s.*(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', devices)
    return ip_addresses
