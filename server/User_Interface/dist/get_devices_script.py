import IpDeviceDiscovery as IDD
import BluetoothUtility as BU
<<<<<<< HEAD
import sys
=======
>>>>>>> fa6011269c983195d8a69830930975d71194778e

def getIpDevices():
    devices = IDD.find_network_devices()
    devices.pop()
    return devices

<<<<<<< HEAD
def getBluetoothDevices():
    return BU.discover()

def getZigbeeDevices():
    return None

def main():
    if( len(sys.argv) != 1):
        devicesToGet = sys.argv[1]
        allDevs = []

        if devicesToGet == "ip":
            allDevs = getIpDevices()

        elif devicesToGet == "bluetooth":
            allDevs = getBluetoothDevices()

        elif devicesToGet == "zigbee":
            pass
            #allDevs = getZigbeeDevices()

        elif devicesToGet == "all":
            allDevs = getIpDevices()
            #allDevs.append(getBluetoothDevices())
            #allDevs.append(getZigbeeDevices())

        # print all the devices for the node server to receive
        for device in allDevs:
            # Name, Ip Address, Mac adddress, Manufacturer
            print(device[1])
            print(device[2])
            print(device[0])
            print(device[3])


main()
=======
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
>>>>>>> fa6011269c983195d8a69830930975d71194778e
