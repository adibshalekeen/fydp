import socket


class SocketController:
    def __init__(self, ip_address='localhost', port_listening=10000):
        self.ip_address = ip_address
        self.port = port_listening

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.server_address = (self.ip_address, self.port)
        self.connected = False

    def start_listening(self):
        listening = True
        print('starting up on %s port %s' % self.server_address)
        self.sock.bind(self.server_address)
        # Listen for incoming connections
        self.sock.listen(1)

        # Wait for a connection
        print('Waiting for a connection...')
        connection, client_address = self.sock.accept()
        while listening:
            try:
                print('connection from %s at %s' % client_address)

                data_incoming = True
                # Receive the data in small chunks and retransmit it
                while data_incoming:
                    data = connection.recv(4096).decode('utf-8')

                    if data:
                        if "CLOSE_CONNECTION" in data:
                            print("Received CLOSE_CONNECTION")
                            data_incoming = False
                        else:
                            print('%s' % data)

                print('no more data from: ', client_address[0])
            except KeyboardInterrupt:
                print('Keyboard interrupt')
                listening = False
                connection.close()
            finally:
                # Clean up the connection
                print('Connection Dropped')
                listening = False
                connection.close()

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
                self.sock.close()