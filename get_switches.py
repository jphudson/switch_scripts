#!/usr/bin/env python
__author__ = "John Hudson"
__credits__ = ["10flow"]
__date__ = "05-07-19"

'''
    Gets a list of IPs that respond to ping in a certain ip address range.
    
    I generally use this to find new devices that were set up in a pinch and were not documented.  
    I also use it for building an initial list of devices if a subnet of switches are not documented.
'''

import datetime
import os

# File creation
now = datetime.datetime.now()
date = str(now.month) + '-' + str(now.day) + '-' + str(now.year)
filename = "switch-list-" + date + ".txt"
f = open(filename, "w")

# You can substitute this next part out for code that calculates by the subnet mask 
# fairly easily, but I find this is a bit easier to read if you have other
# people that need to look at the code and modify it but don't have strong subnetting 
# skills.  They can easily check to see what ip they want to start and what ip they want
# to end with.
beginingIP = "10.0.0.1"
endingIP = "10.0.3.255"

# IMPORTANT: doesn't handle a change in the first or second octet
# Ex. 10.10.X.X will only change the X's
endingCondition = False
def getNextIP (ipAddress):
    global endingCondition
    ip = ipAddress.split(".")
    if ip[3] == '255':
        ip[3] = 0
        ip[2] = int(ip[2]) + 1
    else:
        ip[3] = int(ip[3]) + 1
    if ipAddress == endingIP:
        endingCondition = True
    return ip[0] + '.' +  ip[1] + '.' + str(ip[2]) + '.' + str(ip[3])

# Start pinging ip range
currentIP = beginingIP
while not endingCondition:
    # The ping code comes from 10flow on stack overflow.  They use ping but I'm partial to 
    # fping.  This is a lot quicker than using their commands as well but it does lend
    # itself to a false negative.
    response = os.system("fping -t 500 " + currentIP + ' >/dev/null')
    if response == 0:
        f.write(currentIP + "\n")
    currentIP = getNextIP(currentIP)

f.close()
