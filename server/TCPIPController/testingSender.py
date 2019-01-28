import SocketMessageSender as SMC
import IpDeviceDiscovery as IDD
import CSVController as csvCtrl

import time

devices = [["mac 1", "manf 1", "name 1", "ip 1"], ["mac 2", "manf 2", "name 2", "ip 2"], ["mac 3", "manf 3", "name 3", "ip 3"]]
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
        doMapAct = True
        if len(devices) == 0:
            print("List of devices is empty. Run 'Find network devices' to update the list of devices.")
            continue
        while(doMapAct):
            print("Select a mapping action:")
            print("1. Add a mapping")
            print("2. Delete a mapping")
            print("3. Modify a mapping")
            print("4. See current mapping")
            print("5. Exit mapping modification")
            mapAct = input()
            cont = csvCtrl.CSV_Controller()
            
            mapActVal = 0
            try:
                mapActVal = int(mapAct)
                if mapActVal > 5 or mapActVal < 1:
                    print("Enter a valid option")
                    continue
            except ValueError:
                print("Please enter an integer...")
                continue

            if mapActVal == 5:
                doMapAct = False
            elif mapActVal == 4 or mapActVal == 3 or mapActVal == 2:
                contents = cont.get_file_contents()
                for index, line in enumerate(contents):
                    print(index, line)

                if mapActVal == 3:
                    deviceMac = input("Enter the Mac address of the device you wish to modify in the form 'AA:55:AA:55:AA:55': ")
                    deviceIP = input("Enter the new IP address of the device")
                    cont.modify_entry(deviceIP, deviceMac)
                if mapActVal == 2:
                    mapDelete = input("Select the index of the mapping to delete")
                    try:
                        mapDelVal = int(mapDelete)
                        cont.delete_entry(mapDelVal)
                    except ValueError:
                        print("Please enter an integer...")
                        continue
            elif mapActVal == 1:
                for index, device in enumerate(devices):
                    print("%d - IP: %s, Name: %s, MAC: %s, Manufacturer: %s" % (index, device[3], device[2], device[0], device[1]))

                if mapActVal == 1:
                    source = input("Select a source input: ")
                    dest = input("Select a destination output: ")
                    try:
                        sourceIndex = int(source)
                        destIndex = int(dest)
                        print(len(devices))
                        cont.add_entry([[devices[sourceIndex][3], devices[sourceIndex][0], devices[destIndex][3], devices[destIndex][0]]])
                    except ValueError:
                        print("Please enter an integer")
                        time.sleep(1)
                        continue

    elif path == 3:
        device_to_connect = input("Select the number of a device to connect to:")
        sender = SMC.SocketMessageSender(ip_address=devices[int(device_to_connect)][2])
        value = 0;

        while not value:
            message = input()
            value = sender.send_data(message)
