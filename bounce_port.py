'''
	Pings a group of devices and if any of them fail to respond the script attempts to
	log into the switch and bounce the port

	Had a group of legacy devices that periodically would lose their ip address.  
	Bouncing the port would resolve the issue 
'''

import subprocess, os
from netmiko import ConnectHandler
from getpass import getpass
import time

'''
output supression for subprocess.call comes from stackoverflow user jdi 
on thread named How to hide output of subprocess in Python 2.7
'''

'''
	Note: Since these are dictionaries they aren't in a particular order when the for loop is run

	Will likely convert this info into a yaml file so it's a little less clunky and
	that way I can have an argument when running the switch to select a yaml file incase I have
	different lists that need to use the script
''' 

# 'Device name':'Device ip address to ping'
device_list = {
	'Device_1':'10.0.0.5',
	'Device_2':'10.0.0.6',
	'Device_3':'10.0.0.7'
	}
# 'Device ip address':'Switch ip address'
switch_map = {
	'10.0.0.5':'172.16.0.5',
	'10.0.0.6':'172.16.0.6',
	'10.0.0.7':'172.16.0.7'
	}
# 'Device ip':'port'
port_map = {
	'10.0.0.5':'fa0/1',
	'10.0.0.6':'fa0/2',
	'10.0.0.7':'fa0/3'
	}

platform = 'cisco_ios'
username = 'your_username' #alternativly can ask for username using raw_input("Enter Username: ")
password = getpass("Enter Password: ")

def bounce_port(ip_addr, port):
	'''
		Attempts to log onto the switch and then bounce the port
	'''
	print ("  Connecting to switch...")
	device = ConnectHandler(device_type=platform, ip=ip_addr, username=username, password=password)
	print ("  connected")
	commands = ['interface ' + port, 'shut'] 
	device.send_config_set(commands)
	print ("  shut port down")
	time.sleep(2) #may need to vary depending how long the device needs to wait before being enabled again
	commands = ['interface ' + port, 'no shut']
	device.send_config_set(commands)
	print ("  no shut port")
	device.disconnect()
	print ("  disconnected")

for machine in device_list:
	'''
		Attempts to ping the device.  If ping fails it calls bounce_port then waits before trying to 
		ping again.
	'''
	FNULL = open(os.devnull, 'w')
	ping_command = subprocess.call(['ping', '-c', '1', device_list[machine]], stdout=FNULL, stderr=subprocess.STDOUT)
	if ping_command == 0:
		print (machine + " UP")
	else:
		print "PING FAILURE FOR " + machine
		if (switch_map[device_list[machine]] == 'none'):
			print "  NO SWITCH INFO FOR " + machine
		else:
			print "  Attempting to bounce port"
			port = port_map[device_list[machine]]
			switch_ip = switch_map[device_list[machine]]
			bounce_port(switch_ip, port)
			time.sleep(10)  #waits for device to get the ip address before trying to ping again
			ping_command = subprocess.call(['ping', '-c', '2', device_list[machine]], stdout=FNULL, stderr=subprocess.STDOUT)
			if (ping_command == 0):
				print (machine + " UP")
			else:
				print ("  PORT BOUNCE UNSUCCESSFUL")	
	print