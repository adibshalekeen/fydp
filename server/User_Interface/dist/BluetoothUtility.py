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
    child = pexpect.spawn("bluetoothctl", echo = False)
    child.sendline("power on")
    child.expect(["Changing power on succeeded"])
    child.sendline("agent on")
    child.expect(["Agent registered"])
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
    print("Scanning...")
    child.expect(mac_addr)
    child.sendline("trust " + mac_addr)
    print("Trusting...")
    child.sendline("pair " + mac_addr)
    print("Pairing")
    result = child.expect(["Connected: no", "AlreadyExists", "not available"], timeout = 30)
    if result == 0:
        child.sendline("connect " + mac_addr)
        child.expect(["ServicesResolved: yes", "Error.Failed"], timeout = 30)
        print("connected")
    else:
        print("Failed pairing")

# aplay -D bluealsa:HCI=hci0,DEV=2C:41:A1:07:71:E0,PROFILE=a2dp PinkPanther30.wav
def playSong(song_num, mac_addr):
    song_number = int(song_num)
    music_files = glob('./dist/*.wav')
    dev = "bluealsa:HCI=hci0,DEV=%s,PROFILE=a2dp" % mac_addr

    if song_number > (len(music_files) - 1) or (song_number < 0):
        # print("Song index is out of range")
        return

    # print("Playing song number %s: %s" % (song_number, music_files[song_number][2:]))
    playback = subprocess.run(["aplay", "-D", dev, music_files[song_number][2:], " &"])

def getSongListLength():
    print(len(glob('./dist/*.wav')))

def stopSong():
    playback = subprocess.run(["pkill", "aplay"])

# amixer -D bluealsa sset "Bose QuietComfort 35 - A2DP" 50%
def changeVolume(vol_level, device_name):
    print("here setting %s %s".format(changeVolume, vol_level))
    subprocess.run(["amixer", "-D", "bluealsa", "sset", "\"%s - A2DP" % device_name, "%s%%" % vol_level])
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
