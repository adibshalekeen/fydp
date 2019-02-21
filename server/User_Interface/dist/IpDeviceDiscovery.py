import subprocess
import re
import os


# Function to find the IP connected devices on the network
def find_network_devices(debug=False):

    # Running local device ip settings command on linux is 'ifconfig' and
    # on windows is 'ipconfig'
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

    # nmap command on linux requires superuser
    processToRun = ['sudo', 'nmap', '-sn', userIpAddress] if os.name == "posix" else ['nmap', '-sn', userIpAddress]

    if debug:
        print("Running command \'%s\'" % processToRun)

    response = subprocess.run(processToRun, stdout=subprocess.PIPE)

    # Returned console output from the nmap command
    devices = response.stdout.decode('utf-8')

    if debug:
        for ip in ip_addresses:
            print(ip)

    # Regular expression to capture IP address, MAC address, Device name and Manufacturer
    ip_addresses = re.findall('Nmap.*for\s([a-zA-Z0-9.\-]*)\s.*(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*\n.*\n.*?:\s(.*?)\s\(([a-zA-Z0-9\(\)\s]*)\)', devices)
    return ip_addresses