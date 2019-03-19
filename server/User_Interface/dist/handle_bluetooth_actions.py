import BluetoothUtility as BU
import sys

# 1 = action, 2 = mac, 3 = variable
def main():
    if( len(sys.argv) != 1):
        action = sys.argv[1]

        if action == "connect":
            try:
                BU.connectDevice(sys.argv[2])
            except:
                print("Failed to connect")
        elif action == "playsong":
            BU.playSong(sys.argv[2], sys.argv[3])
        elif action == "stopsong":
            BU.stopSong()
        elif action == "getsonglistlength":
            BU.getSongListLength()
        elif action == "prevsong" or action == "nextsong":
            BU.stopSong()
            BU.playSong(sys.argv[2], sys.argv[3])
        elif action == "volumeup" or action == "volumedown":
            BU.changeVolume(sys.argv[2], sys.argv[3])

main()
