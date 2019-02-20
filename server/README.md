Requires the following packages:
```sh
$ sudo apt install python3 pip3 nodejs npm
$ sudo pip3 install rpi.gpio
$ npm install express
```

For any Python scripts, to use the GPIO pins you must set the mode to be BCM.

# Packet Structure
For the message communication between our devices, we will always be listening and sending to port 10000. We will also
have a standard packet structure to make parsing a lot easier. The structure will be the following:

SOURCEIP|ACTIONID
eg: 192.168.128.155|GESTURE_UP

The above packet will be deciphered in a LUT which will provide a destination IP and
destination ACTIONID.
