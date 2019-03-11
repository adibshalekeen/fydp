import bluetooth as bt

class BTdevice(object):
    def __init__(self, mac_addr):
        self.mac_addr = mac_addr

    def open_socket(self, port=1):
        self.socket = bt.BluetoothSocket(bt.RFCOMM)
        self.socket.connect((self.mac_addr, port))

    def send_msg(self, msg):
        self.socket.send(msg)

    def close_socket(self):
        self.socket.close()

