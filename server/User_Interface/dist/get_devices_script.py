import IpDeviceDiscovery as IDD
import BluetoothUtility as BU

devices = IDD.find_network_devices()
devices.pop()

bDevs = BU.discover()

for device in devices:
    # Name, Ip Address, Mac adddress, Manufacturer
    print(device[1])
    print(device[2])
    print(device[0])
    print(device[3])

for device in bDevs:
    # Name, Ip Address, Mac adddress, Manufacturer
    print(device[1])
    print(device[2])
    print(device[0])
    print(device[3])
