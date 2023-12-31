#!/bin/bash
cd /home/pi/greenhouse
nohup python3 monitor.py > /dev/null &
nohup python3 server.py > /dev/null &
