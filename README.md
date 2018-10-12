README.md

PyScan is a fully functioning nmap style scanning tool written in the Python scripting language. It combines a variety of different features and scanning techniques to find open and exposed ports on network hosts. It operates via command line switches and multiple scans can be performed sequentially by simply including multiple switches. 

October 4, 2018
Changed the traceroute function to operate using Python libaries insead of relying on a subprocess call (which was kind of cheating). Traceroute now works and is faster than running a subprocess call. This also allows for more flexibility across platforms as all OS's treat traceroute and its switches differently.

October 3, 2018
A work in progress TCP/UDP/ICMP port scanning tool written in Python. This tool uses many switches and inputs similar to nmap. Scapy must be installed and configured correctly for UDP scanning to work properly. Cross-platform functionality has been tested and this tool should work both on Windows or Linux platforms. 

TODO:
Rewrite ICMP ping function to operate using Scapy but not print all of scapy's noisy output to the shell. This is hard since scapy functions return 'NoneType' objects which can't be parsed in Python. Another option would be to find another library that can construct and send an ICMP packet to replicate ping functionality.

Use the threading library and configure PyScan to use threading to speed up scans by scanning multiple hosts at the same time. This will significantly speed up overall speed times, especially UDP scans. 

Fix args.ports if statement where portrange is defined as "1-65535" but never utilized. Rename to range and double check the argparser.
