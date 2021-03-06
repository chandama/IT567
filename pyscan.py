#---------------------------------------------------------------------------------
# 
# Name: pyscan.py
# Description: Improved version of nmap.py with increased functionality
# Date: Octover 3, 2018
# Author: Chandler Taylor
# Github: https://github.com/chandama/IT567.git
# Sources: 
#	https://www.phillips321.co.uk/2014/08/12/python-port-scanner-nmap-py/
#	https://stackoverflow.com/questions/29011455/python-script-for-traceroute
#		-and-printing-the-output-in-file-shows-error-oserro
#	https://gist.github.com/amitsaha/8879445
#
#---------------------------------------------------------------------------------

#!/usr/bin/env python
import socket
import subprocess
import sys
import argparse
from datetime import datetime
try:
	from scapy.all import *
except:
	pass


#Set socket timeout to speed up scan (lower is faster)
#Values lower than 0.005 result in missed ports
socket.setdefaulttimeout(0.009)

def main():
    parser = argparse.ArgumentParser(description='portscan.py - Replicates limited nmap functionality in python')
    parser.add_argument('-sS', '--tcpscan', action='store_true', help='Enable this for TCP scans')
    parser.add_argument('-sU', '--udpscan', action='store_true', help='Enable this for UDP scans (must be ran as super user!)')
    parser.add_argument('-sI', '--icmpscan', action='store_true', help='Enable this for ICMP scans')
    parser.add_argument('-tr', '--traceroute', action='store_true', help='Traceroute')
    parser.add_argument('-p', '--ports', default='1-1024', help='Range or list of ports you want to scan')
    parser.add_argument('-t', '--targets', help='The target(s) or CIDR subnet you want to scan (192.168.0.0/24)')
    if len(sys.argv)==1: parser.print_help(); sys.exit(0)
    args = parser.parse_args()

    targets=[]
    #Call appropriate CIDR or iprange decoding functions to produce an array of IPs to scan
    if args.targets:
        if '/' in args.targets:
            targets = returnCIDR(args.targets)
        elif '-' in args.targets:
            targets = iprange(args.targets)
        else:
            try: targets.append(socket.gethostbyname(args.targets))
            except: errormsg("Failed to get IP address from hostname")

    #If just - is entered for ports, scan all possible ports
    if args.ports == '-':
        portRange = '1-65535'
    #If a port range is entered, parse the range
    ranges = (x.split('-') for x in args.ports.split(","))
    ports = [i for r in ranges for i in range(int(r[0]), int(r[-1]) + 1)]

    aliveHosts=0
    openPorts=0

    for target in targets:
        #Scan start time
        t1 = datetime.now()
        reply = 0
        #First check that host is active performing a quick preliminary ICMPscan
        #before running the other scans and filling the screen with empty scan results
        #If ICMPscan returns 0, report inactive host and move on to next target
        if ICMPscan(target,reply)==1:
        	aliveHosts+=1
	        if args.tcpscan:
	    		openPorts+=TCPscan(ports,target,t1)
	        if args.udpscan:
	            UDPscan(ports,target,t1)
	    	if args.traceroute:
	    		traceroute(target)
    	else:
    		print target,"is down"
        if args.icmpscan:
        	if ICMPscan(target,reply) == 1:
        		aliveHosts+=1
        		print target,"is up"

        #Scan finish time
        t2 = datetime.now()
        total = t2 - t1

	#Print scan results to screen 
    print'\n\n','-'*60,'\nSCAN RESULTS\n'
    print'Hosts scanned:',len(targets)
    print'Hosts active:',aliveHosts
    if args.tcpscan or args.udpscan:
	    print'Ports scanned:',len(ports)*aliveHosts
	    print'Open ports:',openPorts
    print'-'*60

def TCPscan(ports,target,t1):
    #Print banner information for host
    print'-'*60,'\nScanning',target,'for open TCP ports...','\n','-'*60
    print'Port\t\tProtocol\tStatus\tElapsed Time\n','-'*60
    try:
        total_ports = 0
        for portnum in ports:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            result = sock.connect_ex((target,portnum))
            if result == 0:
                interval = datetime.now() - t1
                #Print out port number, open, and the time at which it was found
                print"{}\t\tTCP\t\tOpen".format(portnum),"\t",interval
                total_ports+=1
            sock.close()
        #Print time to scan to screen
        total = datetime.now()-t1
        print total_ports, "open ports found in", total, "seconds"
        return total_ports
    except KeyboardInterrupt:
        print"You pressed Ctrl+C"
        sys.exit()
    except socket.gaierror:
        print"Hostname coult not be resolved"
        sys.exit()
    except socket.error:
        print"Exception: socket.error - Couldn't connect to server"
        sys.exit() 

def UDPscan(ports,target,t1):
    try:
	  	print'-'*60,'\nScanning',target,'for open UDP ports...','\n','-'*60
		for portnum in ports:
			data = "---TEST DATA---"
			#a = IP(dst=target)/UDP(dport=portnum)
			#The Scapy sr function returns a 'NoneType' variable which makes extracting information impossible
			#Unless there is some built in Scapy function to let you get the specific value of the UDP dport
			#   you will not be able to neatly display/format the Scapy results like the tcp results.
			ans,unans=sr(IP(dst=target)/UDP(dport=(portnum)),timeout=.5)
			print unans.summary()
			#send(a)
			#if UDP in a:
			#	print a[UDP].dport
			#print a.dport
    except KeyboardInterrupt:
        print"You pressed Ctrl+C"
        sys.exit()
    except socket.gaierror:
        print"Hostname coult not be resolved"
        sys.exit()
    except socket.error:
        print"Exception: socket.error - Couldn't connect to server"
        sys.exit()


def ICMPscan(target,reply):
	try:
		icmp = subprocess.Popen(["ping", target, '-n', '1', '-w', '1'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in iter(icmp.stdout.readline,""):
		    #print line
		    if "Reply" in line:
		    	#print target,"is up"
		    	reply = 1
	except:
		pass
	try:
		icmp = subprocess.Popen(["ping", target, '-c', '1', '-W', '1'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in iter(icmp.stdout.readline,""):
		    #print line
		    if "1 received" in line:
		    	#print target,"is up"
		    	reply = 1
	except:
		pass
	return reply
def traceroute(target):
	#From: https://gist.github.com/amitsaha/8879445
  	print'-'*60,'\nPerforming traceroute on',target,'\n','-'*60
	ttl = 1
	while 1:
	    p=sr1(IP(dst=target,ttl=ttl)/ICMP(id=os.getpid()), 
	          verbose=0)
	    # if time exceeded due to TTL exceeded
	    if p[ICMP].type == 11 and p[ICMP].code == 0:
	        print ttl, '->', p.src
	        ttl += 1
	    elif p[ICMP].type == 0:
	        print ttl, '->', p.src
	        break

# Functions for converting port/target ranges and CIDR subnet masks and parsing them
def iprange(addressrange): # converts a ip range into a list
    list=[]
    first3octets = '.'.join(addressrange.split('-')[0].split('.')[:3]) + '.'
    # I modified the copied code to fix out of bounds problems with second address in range.
    """ range(x,x) each x is a split function which takes the arguments before and after 
        the "-" found in the ip range and treats it as an agument. From there it splits the 
        IP address by its "." and grabs the last octet which is the only one that is important
        for making a list of ranges. This is then fed into a for loop creating a list of 
        sequential numbers"""
    for i in range(int(addressrange.split('-')[0].split('.')[3]),int(addressrange.split('-')[1].split('.')[3])+1):
        list.append(first3octets+str(i))
    return list

def ip2bin(ip):
    b = ""
    inQuads = ip.split(".")
    outQuads = 4
    for q in inQuads:
        if q != "": b += dec2bin(int(q),8); outQuads -= 1
    while outQuads > 0: b += "00000000"; outQuads -= 1
    return b

def dec2bin(n,d=None):
    s = ""
    while n>0:
        if n&1: s = "1"+s
        else: s = "0"+s
        n >>= 1
    if d is not None:
        while len(s)<d: s = "0"+s
    if s == "": s = "0"
    return s

def bin2ip(b):
    ip = ""
    for i in range(0,len(b),8):
        ip += str(int(b[i:i+8],2))+"."
    return ip[:-1]

def returnCIDR(c):
    parts = c.split("/")
    baseIP = ip2bin(parts[0])
    subnet = int(parts[1])
    ips=[]
    if subnet == 32: return bin2ip(baseIP)
    else:
        ipPrefix = baseIP[:-(32-subnet)]
        for i in range(2**(32-subnet)): ips.append(bin2ip(ipPrefix+dec2bin(i, (32-subnet))))
        return ips

#Call Main function
if __name__ == '__main__':
    main()