# torcrack

A simple Tor enabled SSH Brute Force attack in Python3.

# requirements

PyFiglet

tqdm

PySocks

Paramiko

tor

# installation

git clone https://github.com/norksec/torcrack.git

pip3 install pyfiglet tqdm pysocks paramiko

apt-get install -y tor

# usage

Make sure the tor service is running:

service tor restart

python3 torcrack.py -t target -p target_port -u username -d dictionary/password_list [-P tor_port (optional)]

# last note

This is a simple proof of concept - don't expect miracles, but it's worked every time I tried it.
