#!/bin/bash
#launch Oscar - need to specify Oscar.py, just 'Oscar' will kill this script too!
pkill -f Oscar.py
cpu_core=$(lscpu | grep On-line | sed -e 's#.*-\(\)#\1#')
nohup taskset -c "${cpu_core}" python3 Oscar.py -i OscarConfig.xml >/dev/null 2>&1 &

