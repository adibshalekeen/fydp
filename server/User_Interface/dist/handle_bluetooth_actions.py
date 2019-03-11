import BluetoothUtility as BU
import sys


def main():
    if( len(sys.argv) != 1):
        action = sys.argv[1]

        if action == "connect":
            BU.connectDevice(sys.argv[2])

main()
