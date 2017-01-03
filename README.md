# torcrack

A simple Tor enabled, threaded SSH Brute Force dictionary attack in Python3.

# requirements

argparse

PyFiglet

PySocks

Paramiko

tor

# installation

git clone https://github.com/norksec/torcrack.git

pip3 install pyfiglet pysocks paramiko argparse

apt-get install -y tor

# usage

Make sure the tor service is running:

service tor restart

python3 torcrack.py -h for commands
