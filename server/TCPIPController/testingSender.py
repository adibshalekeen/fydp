import SocketMessageSender as SMC
import IpDeviceDiscovery as IDD

print("Searching network for devices...")
devices = IDD.find_network_devices()

for index, device in enumerate(devices):
    print("%d - IP: %s, Name: %s, MAC: %s" % (index, device[2], device[1], device[0]))
device_to_connect = input("Select the number of a device to connect to:")
sender = SMC.SocketMessageSender(ip_address=devices[int(device_to_connect)][2])
value = 0;

while not value:
    message = input()
    value = sender.send_data(message)
