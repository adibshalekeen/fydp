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
            ZU.turnOnLight(sys.argv[2], sys.argv[3], sys.argv[4])
        elif action == "lightoff":
            ZU.turnOffLight(sys.argv[2], sys.argv[3], sys.argv[4])
        elif action == "dimlight":
            ZU.dimLight(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], 30)

main()
