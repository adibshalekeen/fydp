import ZigbeeUtility as ZU
import sys

# 1 = action, 2 = mac, 3 = variable
def main():
    if( len(sys.argv) != 1):
        action = sys.argv[1]

        if action == "getapikey":
            try:
                ZU.getApiKey(sys.argv[2])
            except:
                print("Failed to get key")
        elif action == "lighton":
            try:
                ZU.turnOnLight(sys.argv[2], sys.argv[3], sys.argv[4])
            except:
                print("Failed to turn on light")
        elif action == "lightoff":
            try:
                ZU.turnOffLight(sys.argv[2], sys.argv[3], sys.argv[4])
            except:
                print("Failed to turn on light")
        elif action == "dimlight":
            try:
                ZU.dimLight(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], 30)
            except:
                print("Failed to turn on light")

main()
