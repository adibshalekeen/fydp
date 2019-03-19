import pexpect
import sys

#Source switch is: echo "tx 2F:82:10:00" | cec-client RPI -s -d 4
def sendCommand(sourceNum):
    cecController = pexpect.spawn('cec-client RPI -s -d 4', echo = False)
    cecController.expect(["CEC client registered"])
    command = "tx 2F:82:" + str(1) + "0:00"
    print(command)
    cecController.sendline(command)

def main():
    if( len(sys.argv) != 1):
        if(sys.argv[1] == "changesource"):
            sendCommand(sys.argv[2])

if __name__ == '__main__':
    main()
