import IpDeviceDiscovery as IDD
import BluetoothUtility as BU
import sys

def getIpDevices():
    devices = IDD.find_network_devices()
    devices.pop()
    return devices

def getBluetoothDevices():
    devices = []
    try:
        devices = BU.discover()
    except:
        print("Failed to discover devices")
    return devices

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
            btDevs = getBluetoothDevices()

            for bt in btDevs:
                allDevs.append(bt)
            #allDevs.append(getZigbeeDevices())

        # print all the devices for the node server to receive
        for device in allDevs:
            # Name, Ip Address, Mac adddress, Manufacturer
            print(device[1])
            print(device[2])
            print(device[0])
            print(device[3])


main()
