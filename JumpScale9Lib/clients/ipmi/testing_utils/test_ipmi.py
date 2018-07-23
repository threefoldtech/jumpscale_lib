"""Very simple test script for the ipmi client

Add ipmi interfaces data in DATA

Run script: `python3 test_ipmi.py`
"""

import sys

from js9 import j

# list of ipmi hosts
DATA = [
    {
        "bmc": "10.244.62.220",
        "user": "ADMIN",
        "password": "ADMIN",
        "port": 7000,
    },
    {
        "bmc": "10.244.62.220",
        "user": "ADMIN",
        "password": "ADMIN",
        "port": 7001,
    },
    # .... Add as much as you need to test...
]

def main(argv):
    clients = []

    # create ipmi client for each entry in the ipmi host data list
    i = 0
    for d in DATA:
        c = j.clients.ipmi.get(instance="testclient%s" % i, data=d, interactive=False)
        clients.append(c)
        i+=1

    print("printing initial power state...")
    for c in clients:
        print("host %s is: %s" % (c.config.instance, c.power_status()))

    print("turning on...")
    for c in clients:
        c.power_on()
        print("host %s is: %s" % (c.config.instance, c.power_status()))

    print("power cycling...")
    for c in clients:
        c.power_cycle()
        print("host %s is: %s" % (c.config.instance, c.power_status()))

    print("turning off...")
    for c in clients:
        c.power_off()
        print("host %s is: %s" % (c.config.instance, c.power_status()))

    print("Done!")

if __name__ == "__main__":
    main(sys.argv[1:])
