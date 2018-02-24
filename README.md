# rome L1 Driver

## Overview
The rome L1 Driver provides CloudShell Resource Manager with the capability to communicate with switches that are part of the CloudShell inventory.

End users will be able to create routes, configure port settings, and read values from the switch using the CloudShell Portal, Resource Manager client, or the CloudShell API.

The rome L1 Driver package includes:
| File name | Description |
| ------ | ------ |
| ROME.exe | Driver used by CloudShell Server |
| rome_runtime_configuration.json | JSON file enabling additional configuration interface for the driver
| romeResourceConfiguration.xml | An XML file holding all attribute and capabilities of the L1 switches of the same vendor |

### Requirements
The driver is compatible with the following CloudShell versions:
- 7.0 and above

### Supported Devices/Firmwares
The driver has been verified with the following devices and software versions:
- Device_Type - Version/s

### Installation

Follow the instructions in the link below for installation:
http://help.quali.com/Online%20Help/7.0.0.0/Portal/Content/Admn/Cnct-Ctrl-L1-Swch.htm

In step 7 at the above guide, you will need to copy only one exe file, and instead of the runtimeConfig.xml file please copy the rome_runtime_configuration.json file.

### Supported Functionality
*delete the irrelevant ones*
| Feature | Description |
| ------ | ------ |
| AutoLoad | Creates the sub-resources of the L1 switch |
| MapBidi | Creates a bi-directional connection between two ports |
| MapUni | Creates a uni-directional connection between two ports |
| MapClear | Clears any connection ending in this port |
| MapClearTo | Clears a uni-directional connection between two ports |

### Configuration
*add any relevant information about the different keys in the rome_runtime_configuration.json file or remove this section*
| Feature | Description |
| ------ | ------ |
| common_variable.connection_port | TCP Port connection, default is 1234 |

### Known Issues
*add any known issues or remove this section*
