# Mic setup
Enter the following commands into a bash prompt. I'm not sure which commands are unnecessary so just install all of them.

```bash
cd ~
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard/
sudo ./install.sh
sudo reboot
sudo apt install -y mpg123 portaudio19-dev pocketsphinx python-pocketsphinx libpuse-dev
sudo pip3 install pyaudio webrtcvad pocketsphinx respeaker
```

For a demo run script.py as sudo otherwise mic detection won't work.
