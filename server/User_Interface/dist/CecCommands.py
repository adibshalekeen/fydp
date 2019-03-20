import pexpect
import sys

#Source switch is: echo "tx 2F:82:10:00" | cec-client RPI -s -d 4
def sendCommand(sourceNum):
    cecController = pexpect.spawn('cec-client', echo = False)
    result = cecController.expect(["waiting for input"])
    if result == 0:
        command = "tx 2F:82:" + str(sourceNum) + "0:00"
        cecController.sendline(command)
        result = cecController.expect(["15"], timeout = 10)
    else:
        print("Failed to connect to CEC client")

def main():
    if( len(sys.argv) != 1):
        if(sys.argv[1] == "changesource"):
            sendCommand(sys.argv[2])

if __name__ == '__main__':
    main()
