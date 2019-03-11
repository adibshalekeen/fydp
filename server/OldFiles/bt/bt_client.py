import bt_utils as bt
from bt_dev import BTdevice

if __name__ == '__main__':
    devs = bt.discover()
    dev_num = int(input("Enter the number of the device you want to connect to: "))
    dev = devs[dev_num]
    my_device = BTdevice(dev[0])
    my_device.open_socket()
    print("Ready to send.")
    while True:
        msg = input()
        if msg != 'q': my_device.send_msg(msg)
        else: break
    my_device.close_socket()


