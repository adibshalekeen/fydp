import SocketMessageSender as SMC

sender = SMC.SocketMessageSender(ip_address="10.161.35.148")
value = 0;

while not value:
    message = input()
    value = sender.send_data(message)
