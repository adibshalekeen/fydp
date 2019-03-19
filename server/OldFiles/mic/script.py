from respeaker import Microphone
m = Microphone()
while True:
    print('Listening...')
    if m.wakeup('cstar'):
        print('Wake up')
        data = m.listen(duration=5)
        text = m.recognize(data)
        if text:
            print('Text recognized')
            print('Recognized %s' % text)
        else:
            print('No text recognized')
