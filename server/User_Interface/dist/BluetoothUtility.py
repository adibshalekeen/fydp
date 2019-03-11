import bluetooth as bt
from glob import glob
import time
import pexpect
import subprocess
import sys
import re

"""
Prints devices found nearby and returns a list of tuples
"""
def discover():
    devices = []
    devs = bt.discover_devices(duration=5, lookup_names=True)
    for addr, name in devs:
        devices.append([name, "BLUETOOTH", addr, "N/A"])
    return devices

"""
Connects to specified device and returns an open socket
(Effectively opens a serial port)
"""
def connect(mac_addr, port=1):
    sckt = bt.BluetoothSocket(bt.RFCOMM)
    print("Connecting to %s ..." % mac_addr)
    sckt.connect((mac_addr, port))
    print("Connected.")
    return sckt

"""
Connect to the bluetooth speaker device here
2C:41:A1:07:71:E0 - bose
C0:28:8D:46:94:A2 - ue
"""
def connectDevice(mac_addr):
    child = pexpect.spawn("bluetoothctl", echo = False)
    child.sendline("power on")
    child.expect(["Changing power on succeeded"])
    child.sendline("agent on")
    child.expect(["Agent registered"])
    child.sendline("scan on")
    child.expect(mac_addr)
    child.sendline("trust " + mac_addr)
    child.sendline("pair " + mac_addr)
    result = child.expect(["Connected: no", "AlreadyExists", "not available"], timeout = 30)
    if result == 0:
        child.sendline("connect " + mac_addr)
        child.expect(["ServicesResolved: yes", "Error.Failed"], timeout = 30)
        print("connected")
    else:
        print("Failed pairing")


def playSong(song_number, mac_addr):
    args = 'bluealsa:DEV=%s,PROFILE=a2dp,HCI=hci0' % mac_addr
    playback = pexpect.spawn("aplay -D %s %s" % (args, self.music_files[0]), echo=False)

def change_volume(self, increment):
    pexec.spawn(["amixer -D bluealsa sset %s %s" % (self.dev_name, increment)])
#
# class Bluetoothctl:
#     mac_addr = '00:0C:8A:FE:85:72'
#     # Need ' - A2DP' suffix
#     dev_name = 'Bose Colour SoundLink - A2DP'
#
#     def __init__(self):
#         out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
#         self.child = pexpect.spawn("bluetoothctl", echo = False)
#         self.music_files = glob('./*.wav')
#
#     def get_output(self, command, pause = 0):
#         """Run a command in bluetoothctl prompt, return output as a list of lines."""
#         self.child.sendline(command)
#         time.sleep(pause)
#         start_failed = self.child.expect(["bluetooth", pexpect.EOF])
#
#         if start_failed:
#             raise BluetoothctlError("Bluetoothctl failed after running " + command)
#
#         return self.child.before.split(b"\r\n")
#
#     def connect(self, mac_address):
#         try:
#             out = self.get_output("connect " + self.mac_addr, 2)
#         except BluetoothctlError as e:
#             print(e)
#             return None
#
#     def play(self):
#         args = 'bluealsa:DEV=%s,PROFILE=a2dp,HCI=hci0' % self.mac_addr
#         self.playback = pexpect.spawn("aplay -D %s %s" % (args, self.music_files[0]), echo=False)
#
#     def change_volume(self, increment):
#         pexec.spawn(["amixer -D bluealsa sset %s %s" % (self.dev_name, increment]))
