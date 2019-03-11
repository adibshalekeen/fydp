# Stole from https://gist.github.com/ofekp/539ce199a96e6a9ace2c1511cc7409ce
# because it was easier to migrate to Python 3

from glob import glob
import time
import pexpect
import subprocess
import sys
import re

class BluetoothctlError(Exception):
    pass


class Bluetoothctl:
    mac_addr = '00:0C:8A:FE:85:72'
    # Need ' - A2DP' suffix
    dev_name = 'Bose Colour SoundLink - A2DP'

    def __init__(self):
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.child = pexpect.spawn("bluetoothctl", echo = False)
        self.music_files = glob('./*.wav')

    def get_output(self, command, pause = 0):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.sendline(command)
        time.sleep(pause)
        start_failed = self.child.expect(["bluetooth", pexpect.EOF])

        if start_failed:
            raise BluetoothctlError("Bluetoothctl failed after running " + command)

        return self.child.before.split(b"\r\n")


    def connect(self, mac_address):
        try:
            out = self.get_output("connect " + self.mac_addr, 2)
        except BluetoothctlError as e:
            print(e)
            return None

    def play(self):
        args = 'bluealsa:DEV=%s,PROFILE=a2dp,HCI=hci0' % self.mac_addr
        self.playback = pexpect.spawn("aplay -D %s %s" % (args, self.music_files[0]), echo=False)

    def change_volume(self, increment):
        pexec.spawn(["amixer -D bluealsa sset %s %s" % (self.dev_name, increment]))


