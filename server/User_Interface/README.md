# User Interface for Control star
This is the user interface that will be used to configure the device and gesture mapping for the program. The interface runs off Node.js and you should refer to this guide to set up the dependencies: https://blog.cloudboost.io/how-to-run-a-nodejs-web-server-on-a-raspberry-pi-for-development-3ef9ac0fc02c

Run the following to install Node.js:
```
sudo su;
wget -O - https://raw.githubusercontent.com/audstanley/NodeJs-Raspberry-Pi/master/Install-Node.sh | bash;
exit;
node -v;
```

The backend script handling is processed on Python3 and will require the relevant versions of packages. Make sure to use *pip3 install* to ensure the right version is installed.

# Functionalities of Interface
The interface will be able to do the following:
* Discover devices connected to your network on the IP, Bluetooth and Zigbee bands
* Save the discovered devices with reference to their name, IP and MAC address
* Connect to a bluetooth device defined in the saved devices
* Create a mapping between incoming IP signals to outgoing IP, Bluetooth or Zigbee bands

# Notes
Make sure to install some of the following packages:
```
sudo apt-get install bluealsa pulseaudio pulseaudio-module-bluetooth
```
* bluealsa - Playback of music to a connect BT device
* pulseaudio - Controls output routing for sounds
* pulseaudio-module-bluetooth - Controls protocol communicating with BT devices

```
pip3 install pexpect bluetooth
```
* pexpect - Used for CLI command sending and receiving
* bluetooth - Used for BT device discovery but could also use bluetoothctl built in but this is easier to process
