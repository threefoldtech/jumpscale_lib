# Get a capacity report from an Ubuntu node

## Step 1: Open Jumpscale

Jumpscale provides a System Abstraction Layer (sal) for Ubuntu. In that sal a property is provided from which the report can be generated.

Start the Jumpscale9 Python interpreter.
If not installed, the jumpscale bash utilities can be used to install JS9 (https://github.com/Jumpscale/bash)
```bash
js9
```

## Step2: Call the capacity report

The capacity property of the Ubuntu sal has a report method that returns the capacity report.

```python
# Fetch the report
report = j.sal.ubuntu.capacity.report()

# Print the CRU (core units)
print(report.CRU)
4

# Print the MRU (total memory in GiB)
print(report.MRU)
15.57

# Print the HRU (total hard drive capacity in GiB)
print(report.HRU)
0

# Print the SRU (total solid state capacity in GiB)
print(report.SRU)
238.47

# Print the full report
print(report)
{"motherboard": [{"version": "A00", "asset_tag": "Not Specified", "serial": "/6N7NW32/CN129667780257/", "manufacturer": "Dell Inc.", "name": null}], "disk": [{"model": null, "sector_size": null, "rotation_state": null, "name": "/dev/sr0", "type": "CDROM", "user_capacity": null, "device_id": null, "serial": null, "size": "1073741312", "firmware_version": null, "form_factor": null}, {"model": "Micron 1100 SATA 256GB", "sector_size": "512 bytes logical, 4096 bytes physical", "rotation_state": "Solid State Device", "name": "/dev/sda", "type": "SSD", "user_capacity": "256,060,514,304 bytes [256 GB]", "device_id": "5 00a075 11712156c", "serial": "17161712156C", "size": "256060514304", "firmware_version": "M0DL003", "form_factor": "M0DL003"}], "processor": [{"version": "Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz", "id": "E9 06 08 00 FF FB EB BF", "thread_nr": "4", "manufacturer": "Intel(R) Corporation", "serial": "To Be Filled By O.E.M.", "core_nr": "2", "speed": "2600 MHz"}], "memory": [{"size": "No Module Installed", "width": "Unknown", "asset_tag": "Not Specified", "serial": "Not Specified", "manufacturer": "Not Specified", "speed": "Unknown"}, {"size": "16384 MB", "width": "64 bits", "asset_tag": "0F172300", "serial": "17594AB3", "manufacturer": "Micron", "speed": "2400 MHz"}]}

# Print prettified report
report = j.sal.ubuntu.capacity.report(indent=2)
print(report)
{
  "motherboard": [
    {
      "version": "A00",
      "asset_tag": "Not Specified",
      "serial": "/6N7NW32/CN129667780257/",
      "manufacturer": "Dell Inc.",
      "name": null
    }
  ],
  "disk": [
    {
      "model": null,
      "sector_size": null,
      "rotation_state": null,
      "name": "/dev/sr0",
      "type": "CDROM",
      "user_capacity": null,
      "device_id": null,
      "serial": null,
      "size": "1073741312",
      "firmware_version": null,
      "form_factor": null
    },
    {
      "model": "Micron 1100 SATA 256GB",
      "sector_size": "512 bytes logical, 4096 bytes physical",
      "rotation_state": "Solid State Device",
      "name": "/dev/sda",
      "type": "SSD",
      "user_capacity": "256,060,514,304 bytes [256 GB]",
      "device_id": "5 00a075 11712156c",
      "serial": "17161712156C",
      "size": "256060514304",
      "firmware_version": "M0DL003",
      "form_factor": "M0DL003"
    }
  ],
  "processor": [
    {
      "version": "Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz",
      "id": "E9 06 08 00 FF FB EB BF",
      "thread_nr": "4",
      "manufacturer": "Intel(R) Corporation",
      "serial": "To Be Filled By O.E.M.",
      "core_nr": "2",
      "speed": "2600 MHz"
    }
  ],
  "memory": [
    {
      "size": "No Module Installed",
      "width": "Unknown",
      "asset_tag": "Not Specified",
      "serial": "Not Specified",
      "manufacturer": "Not Specified",
      "speed": "Unknown"
    },
    {
      "size": "16384 MB",
      "width": "64 bits",
      "asset_tag": "0F172300",
      "serial": "17594AB3",
      "manufacturer": "Micron",
      "speed": "2400 MHz"
    }
  ]
}

```
