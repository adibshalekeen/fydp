import SocketMessageSender as SMC

sender = SMC.SocketMessageSender(ip_address="10.161.35.148")

while True:
    message = input()
    sender.send_data(message)
