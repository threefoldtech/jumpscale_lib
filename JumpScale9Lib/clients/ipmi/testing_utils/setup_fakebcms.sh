#!/bin/bash

# This script creates fake bcms (ipmi hosts) in a tmux session `ipmis`
# This script presumes you have cloned the pghmi repo in the `~/` directory
# Either clone the orginal repo and use the fakebcm server there (bin/fakebmc). It's in python 2 so adapt if needed
# `cd ~; git clone https://github.com/openstack/pyghmi.git`
# Or clone my fork which has adapted the fakebcm server to python3 and changed login to `ADMIN`/`ADMIN` from `admin`/`password`
# `cd ~; git clone https://github.com/chrisvdg/pyghmi.git`

# change the command if cloned elsewhere to call the correct path

# Join the tmux session where the servers are created: `tmux attach -t ipmis`
# Kill the tmux session: tmux kill-session -t ipmis

tmux has-session -t ipmis

if [ $? != 0 ]
then
    SERVERS=5
    tmux new -s ipmis -d
    port=7000

    for i in $(eval echo {1..$SERVERS})
    do
        windowname="ipmi-$i"
        tmux new-window -n $windowname -t ipmis
        tmux send-keys -t ipmis "~/pyghmi/bin/fakebmc --port $port" C-m
        ((port++))
    done

fi
