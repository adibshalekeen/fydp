import SocketController as SC

controller = SC.SocketController()

while True:
    message = input()
    controller.send_data(message)