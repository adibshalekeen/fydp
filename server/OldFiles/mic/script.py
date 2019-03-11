from respeaker import Microphone
m=Microphone()
if (m.wakeup('respeaker')):
    print("wake up")
