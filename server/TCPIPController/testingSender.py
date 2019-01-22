import SocketMessageSender as SMC

sender = SMC.SocketMessageSender()

while True:
    message = input()
    sender.send_data(message)