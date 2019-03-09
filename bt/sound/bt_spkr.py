from glob import glob
import subprocess

class Speaker(object):
    mac_addr = '00:0C:8A:FE:85:72'
    # Need ' - A2DP' prefix
    dev_name = 'Bose Colour SoundLink - A2DP'

    def __init__(self):
        self.proc = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.music_files = glob('./*.wav')

    def connect(self, mac_addr):
        # self.mac_addr = mac_addr
        self.communicate(' '.join(['connect', self.mac_addr]))

    def communicate(self, cmd):
        # self.proc.communicate(cmd)[0]
        self.proc.stdin.write(cmd)

    def play(self):
        args = 'bluealsa:DEV=%s,PROFILE=a2dp,HCI=hci0' % self.mac_addr
        self.playback = subprocess.Popen(['aplay', '-D', args, self.music_files[0]], shell=True)

    def change_volume(self, increment):
        subprocess.Popen(['amixer', '-D', 'bluealsa', 'sset', self.dev_name, increment])

