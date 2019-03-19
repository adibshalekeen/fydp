# Mic setup
Enter the following commands into a bash prompt. I'm not sure which commands are unnecessary so just install all of them.


```bash
cd ~
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard/
sudo ./install.sh
sudo reboot
sudo apt install -y mpg123 portaudio19-dev pocketsphinx python-pocketsphinx libpulse-dev
sudo pip3 install pyaudio webrtcvad pocketsphinx respeaker
```


For a demo run script.py as sudo otherwise mic detection won't work.

## Custom Hotword Detection
To detect custom hotwords, there are two key files to edit. They are both located in `/usr/local/lib/python3.5/dist-packages/respeaker/pocketsphinx-data`

First, add the phonetics for the word into dictionary.txt. There is a complete list of words broken up into their phonetics at <https://raw.githubusercontent.com/respeaker/pocketsphinx-data/master/dictionary.txt>.

Then, add the word to keywords.txt and indicate some sort of power level. Not entirely sure what this does but I just used 1e-40.
