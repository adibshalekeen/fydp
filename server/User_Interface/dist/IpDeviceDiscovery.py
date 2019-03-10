import subprocess
import re
import sys
import os

def get_my_ip():
    userIpAddress = []
    # Running local device ip settings command on linux is 'ifconfig' and
    # on windows is 'ipconfig'
    if os.name == "nt":
        ipconfigResp = subprocess.run(['ipconfig'], stdout=subprocess.PIPE)
        ipconfigResp = ipconfigResp.stdout.decode('utf-8')
        userIpAddress = re.findall('\s{3}IPv4\sAddress.*\s(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ipconfigResp)
    elif os.name == "posix":
        ipconfigResp = subprocess.run(['ifconfig', 'wlan0'], stdout=subprocess.PIPE)
        ipconfigResp = ipconfigResp.stdout.decode('utf-8')
        userIpAddress = re.findall('inet\s(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ipconfigResp)
    return userIpAddress[0]

# Function to find the IP connected devices on the network
def find_network_devices(debug=False):
    userIpAddress = get_my_ip() + "/24"

    # nmap command on linux requires superuser
    processToRun = ['sudo', 'nmap', '-sn', userIpAddress] if os.name == "posix" else ['nmap', '-sn', userIpAddress]

    if debug:
        print("Running command \'%s\'" % processToRun)

    response = subprocess.run(processToRun, stdout=subprocess.PIPE)

    # Returned console output from the nmap command
    devices = response.stdout.decode('utf-8')

    # Regular expression to capture IP address, MAC address, Device name and Manufacturer
    ip_addresses = re.findall('Nmap.*for\s([a-zA-Z0-9\(\)\s\.\-\'\_]*\s)?.*?(\d*\.\d{1,3}\.\d{1,3}\.\d{1,3}).*\n.*\n.*?:\s(.*?)\s\(([a-zA-Z0-9\(\)\s\.\-\']*?)\)', devices)

    if debug:
        for ip in ip_addresses:
            print(ip)

    return ip_addresses


def main():
    if( len(sys.argv) != 1):
        if(sys.argv[1] == "get_ip"):
            function_code = get_my_ip();
            print(function_code)

main()
