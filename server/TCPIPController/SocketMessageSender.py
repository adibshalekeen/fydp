import socket


class SocketMessageSender:
    def __init__(self, ip_address='localhost', port_listening=10000):
        print("Connecting to %s" % ip_address)
        self.ip_address = ip_address
        self.port = port_listening

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.server_address = (self.ip_address, self.port)
        self.connected = False

    def send_data(self, message):
        if not self.connected:
            self.sock.connect(self.server_address)
            self.connected = True
        try:
            # Send data
            print('sending "%s"' % message)
            self.sock.sendall(message.encode())
        finally:
            if "CLOSE_CONNECTION" in message:
                print('closing socket')
                response = self.sock.recv(256)
                self.sock.close()
                return 1
