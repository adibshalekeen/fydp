import bt_utils as bt

if __name__ == '__main__':
    devs = bt.discover()
    dev_num = input("Enter the number of the device you want to connect to: ")
    dev = devs[dev_num]
    sckt = bt.connect(dev[0])
    print "Ready to send."
    while True:
        msg = raw_input()
        if msg != 'q': sckt.send(msg)
        else: break
    sckt.close()


