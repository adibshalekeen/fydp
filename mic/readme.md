cd ~
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard/
sudo ./install.sh
sudo reboot
sudo apt install -y mpg123 portaudio19-dev pocketsphinx python-pocketsphinx libpuse-dev
sudo pip install pyaudio webrtcvad
git clone https://github.com/respeaker/respeaker_python_library
sudo python respeaker_puthon_library/setup.py develop
sudo script.py
