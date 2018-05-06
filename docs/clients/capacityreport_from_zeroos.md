# Get a capacity report from a Zero-OS node

## Step 1: Attach host to the ZeroTier network of the Zero-OS node

Make sure the Zero-OS node is running. On how to start a Zero-OS node, check the [Zero-OS boot docs](https://github.com/zero-os/0-core/blob/development/docs/booting/README.md)

Zero-OS nodes will run inside a [ZeroTier](https://www.zerotier.com/) network. To access them, the host needs to have access to that ZeroTier network.

Install the ZeroTier tools [from here](https://www.zerotier.com/download.shtml)

Get the network-ID of the ZeroTier network (Can be seen on the Zero-OS main screen).

Join the ZeroTier netwerk
```bash
zerotier-cli join <network-ID>
```

Make sure the host is authorized on the network. (https://my.zerotier.com/network/\<network-id\>)

## Step 2: Get the Zero-OS client in Jumpscale9

Start the Jumpscale9 Python interpreter.
If not installed, the jumpscale bash utilities can be used to install JS9 (https://github.com/Jumpscale/bash)
```bash
js9
```

Get the Zero-OS client
```python
# Omit data when using the config manager
# The config manager will then prompt for the necessary client data.
# In fact this step (step 2) can be skipped when using the config manager
# It will ask for for the client data when `get_node` is called when there is no client for the instance
data = {
    # host is the internal ZeroTier address of the Zero-OS node
    "host": "192.168.191.191"
    # port the Zero-OS node is listening on
    "port": 6379, # This is the default port
    # If the Zero-OS node requires authentication
    # provide a JWT here
    "password_": "<a valid JWT for the Zero-OS node>",
}

cl = j.clients.zero_os.get(instance="node1", data=data) 
```

## Step 3: Get the Zero-OS sal

Jumpscale provides a System Abstraction Layer (sal) for Zero-OS which can be used to get the capacity report from the node.

```python
node = j.clients.zero_os.sal.get_node(instance="node1")
```

The sal will look for a Zero-OS client with the instance name of `node1` and use that to interact with the Zero-OS node.
When only using a single node, `instance` can be omitted and the default instance `main` will be used.
If no Zero-OS client is found for that instance, the config manager will prompt for the client data and create a client for the sal.

## Step 4: Get the report

From the sal we can make a call to get the capacity report.

```python
# Fetch the report
report = node.capacity.report()

# Print the CRU (core units)
print(report.CRU)
4

# Print the MRU (total memory in GiB)
print(report.MRU)
15.65

# Print the HRU (total hard drive capacity in GiB)
print(report.HRU)
1870.56

# Print the SRU (total solid state capacity in GiB)
print(report.SRU)
119.24

# Print the full report
print(report)
{"disk": [{"sector_size": "512 bytes logical, 4096 bytes physical", "model": "ST2000LM015-2E8174", "firmware_version": "SDM1", "serial": "WDZ3AS4C", "size": 2000398934016, "rotation_state": "5400 rpm", "type": "HDD", "device_id": "5 000c50 0a8ca979a", "form_factor": "SDM1", "name": "/dev/sdb", "user_capacity": "2,000,398,934,016 bytes [2.00 TB]"}, {"sector_size": null, "model": null, "firmware_version": null, "serial": null, "size": 8103395328, "rotation_state": null, "type": "HDD", "device_id": null, "form_factor": null, "name": "/dev/sdc", "user_capacity": null}, {"sector_size": null, "model": "KINGSTON RBUSMS180DS3128GH", "firmware_version": "SBFK10D7", "serial": "50026B727304D619", "size": 128035676160, "rotation_state": "Solid State Device", "type": "SSD", "device_id": "5 000000 000000000", "form_factor": "SBFK10D7", "name": "/dev/sda", "user_capacity": "128,035,676,160 bytes [128 GB]"}], "processor": [{"version": "Intel(R) Core(TM) i5-7200U CPU @ 2.50GHz", "speed": "2400 MHz", "serial": "To Be Filled By O.E.M.", "thread_nr": "4", "id": "E9 06 08 00 FF FB EB BF", "manufacturer": "Intel(R) Corporation", "core_nr": "2"}], "motherboard": [{"serial": "Default string", "asset_tag": "Default string", "version": "Default string", "name": null, "manufacturer": "INTEL Corporation"}], "memory": [{"speed": "1600 MHz", "size": "8192 MB", "serial": "0B7DF43D", "asset_tag": "9876543210", "width": "64 bits", "manufacturer": "SK Hynix"}, {"speed": "1600 MHz", "size": "8192 MB", "serial": "03B7519E", "asset_tag": "9876543210", "width": "64 bits", "manufacturer": "SK Hynix"}]}


# prettified report
report = node.capacity.report(indent=2)
print(report)
{
  "disk": [
    {
      "sector_size": "512 bytes logical, 4096 bytes physical",
      "model": "ST2000LM015-2E8174",
      "firmware_version": "SDM1",
      "serial": "WDZ3AS4C",
      "size": 2000398934016,
      "rotation_state": "5400 rpm",
      "type": "HDD",
      "device_id": "5 000c50 0a8ca979a",
      "form_factor": "SDM1",
      "name": "\/dev\/sdb",
      "user_capacity": "2,000,398,934,016 bytes [2.00 TB]"
    },
    {
      "sector_size": null,
      "model": null,
      "firmware_version": null,
      "serial": null,
      "size": 8103395328,
      "rotation_state": null,
      "type": "HDD",
      "device_id": null,
      "form_factor": null,
      "name": "\/dev\/sdc",
      "user_capacity": null
    },
    {
      "sector_size": null,
      "model": "KINGSTON RBUSMS180DS3128GH",
      "firmware_version": "SBFK10D7",
      "serial": "50026B727304D619",
      "size": 128035676160,
      "rotation_state": "Solid State Device",
      "type": "SSD",
      "device_id": "5 000000 000000000",
      "form_factor": "SBFK10D7",
      "name": "\/dev\/sda",
      "user_capacity": "128,035,676,160 bytes [128 GB]"
    }
  ],
  "processor": [
    {
      "version": "Intel(R) Core(TM) i5-7200U CPU @ 2.50GHz",
      "speed": "2400 MHz",
      "serial": "To Be Filled By O.E.M.",
      "thread_nr": "4",
      "id": "E9 06 08 00 FF FB EB BF",
      "manufacturer": "Intel(R) Corporation",
      "core_nr": "2"
    }
  ],
  "motherboard": [
    {
      "serial": "Default string",
      "asset_tag": "Default string",
      "version": "Default string",
      "name": null,
      "manufacturer": "INTEL Corporation"
    }
  ],
  "memory": [
    {
      "speed": "1600 MHz",
      "size": "8192 MB",
      "serial": "0B7DF43D",
      "asset_tag": "9876543210",
      "width": "64 bits",
      "manufacturer": "SK Hynix"
    },
    {
      "speed": "1600 MHz",
      "size": "8192 MB",
      "serial": "03B7519E",
      "asset_tag": "9876543210",
      "width": "64 bits",
      "manufacturer": "SK Hynix"
    }
  ]
}

```
