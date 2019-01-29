import socket
import select
import MappingInterfaceCtrl as mictrl

class HubMessageServer:
    def __init__( self, port ):
        self.port = port;

        self.srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srvsock.bind(("", port))
        self.srvsock.listen(5)

        self.descriptors = []
        self.descriptors.append(self.srvsock)
        print('HubMessageServer started on port %s' % port)
        self.mictrl = mictrl.MappingInterfaceCtrl()

    def run(self):
            while 1:
                # Await an event on a readable socket descriptor
                sread, _, _ = select.select(self.descriptors, [], [], 1)

                # Iterate through the tagged read descriptors
                for sock in sread:
                    # Received a connect to the server (listening) socket
                    if sock == self.srvsock:
                        self.accept_new_connection()
                    else:
                        # Received something on a client socket
                        try:
                            str = sock.recv(256)
                            host, port = sock.getpeername()
                        except ConnectionResetError:
                            print("Connection has been reset")
                            str = b''
                            sread.remove(sock)

                        # Check to see if the peer socket closed
                        if str == b'':
                            str = 'Client left %s:%s\r\n' % (host, port)
                            self.broadcast_string(str.encode(), sock)
                            sock.close
                            self.descriptors.remove(sock)
                        else:
                            newstr = '[%s:%s] %s' % (host, port, str.decode('utf-8'))
                            print(newstr)

                            # Here we will do a lookup to see if the incoming message is any use to us
                            destIp = self.mictrl.get_mapped_addresses(host)
                            print("got %s" % destIp)

                            #self.broadcast_string(newstr.encode(), sock)

    def send_message(self, dest_ip, dest_port=10000, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((dest_ip, dest_port))
        sock.sendall(msg.encode())
        sock.close()

    def broadcast_string( self, str, omit_sock ):
        for sock in self.descriptors:
            if sock != self.srvsock and sock != omit_sock:
                sock.send(str)

        print(str)

    def accept_new_connection( self ):
        newsock, (remhost, remport) = self.srvsock.accept()
        self.descriptors.append(newsock)

        str_to_send = "You're connected to the Python chatserver\r\n"
        newsock.send(str_to_send.encode())
        str = 'Client joined %s:%s\r\n' % (remhost, remport)
        self.broadcast_string(str.encode(), newsock)
