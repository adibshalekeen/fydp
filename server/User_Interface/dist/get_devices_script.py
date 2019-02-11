import IpDeviceDiscovery as IDD

devices = IDD.find_network_devices()

devices.pop()

for device in devices:
    # Name, Ip Address, Mac adddress, Manufacturer
    print(device[1])
    print(device[2])
    print(device[0])
    print(device[3])
