import os
import sys
from os import system as cmd

if not os.geteuid() == 0:
    sys.exit("\nOnly root can run this script\n")

cmd("apt-get update -y && apt upgrade -y")
cmd("apt-get install python3-pip curl wget git unzip dnsutils -y")
cmd("pip3 install --upgrade pip")
cmd("pip3 install rich")
