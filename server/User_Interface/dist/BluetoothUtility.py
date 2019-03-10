import bluetooth as bt

"""
Prints devices found nearby and returns a list of tuples
"""
def discover():
    devices = []
    devs = bt.discover_devices(duration=5, lookup_names=True)
    for addr, name in devs:
        devices.append([name, "BLUETOOTH", addr, "N/A"])
    return devices

"""
Connects to specified device and returns an open socket
(Effectively opens a serial port)
"""
def connect(mac_addr, port=1):
    sckt = bt.BluetoothSocket(bt.RFCOMM)
    print("Connecting to %s ..." % mac_addr)
    sckt.connect((mac_addr, port))
    print("Connected.")
    return sckt
