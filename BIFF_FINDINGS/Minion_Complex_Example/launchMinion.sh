#!/bin/bash

#launch Minion - need to specify Minion.py, just 'Minion' will kill this script too!
pkill -f Minion.py
cpu_core=$(lscpu | grep On-line | sed -e 's#.*-\(\)#\1#')

{   echo "SUT-MINION=starting Minion"
    echo "SUT-MINION-1=starting Minion"
    echo "SUT-MINION-actors=starting Minion"
} > minion_status.log

nohup taskset -c "${cpu_core}" python3 Minion.py -i Vision-SUT-1.xml >/dev/null 2>&1 &
nohup taskset -c "${cpu_core}" python3 Minion.py -i Vision-SUT.xml >/dev/null 2>&1 &
nohup python3 Minion.py -i Vision-SUT-actors.xml >/dev/null 2>&1 &
# nohup python3 Minion.py -i Vision-LP-1.xml >/dev/null 2>&1 &
# nohup python3 Minion.py -i Vision-LP.xml >/dev/null 2>&1 &
