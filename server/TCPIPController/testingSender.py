import SocketMessageSender as SMC
import IpDeviceDiscovery as IDD

import time

while(1):
    print("What would you like to do?")
    print("1. Find network devices")
    print("2. Update mapping of devices")
    print("3. Start sender")
    path = input()
    try:
        num = int(path)
        if(num > 3 or num < 1):
            print("Please select a valid option...")
            time.sleep(1)
            continue
    except ValueError:
        print("Please enter an integer...")
        time.sleep(1)
        continue

    path = int(path)
    if path == 1:
        print("Searching network for devices... (Note: This may take a while for dense networks)")
        devices = IDD.find_network_devices()

        for index, device in enumerate(devices):
            print("%d - IP: %s, Name: %s, MAC: %s, Manufacturer: %s" % (index, device[3], device[2], device[0], device[1]))
    elif path == 2:
        pass

    elif path == 3:
        device_to_connect = input("Select the number of a device to connect to:")
        sender = SMC.SocketMessageSender(ip_address=devices[int(device_to_connect)][2])
        value = 0;

        while not value:
            message = input()
            value = sender.send_data(message)
