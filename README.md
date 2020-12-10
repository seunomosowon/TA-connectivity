——-
## Table of Contents

### OVERVIEW

- About the TA-connectivity
    - Scripts and binaries
- Release notes
    - About this release
    - New features
    - Known issues
    - Third-party software attributions
    - Support and resources
    - Older Releases
- Support and resources

### INSTALLATION AND CONFIGURATION

- Hardware and software requirements
    - Hardware requirements
    - Software requirements
    - Splunk Enterprise system requirements

- Installation steps
    - Deploy to single server instance
    - Deploy to distributed deployment
    - Deploy to Splunk Cloud
    - Configure TA-connectivity
        - Test availability via Ping.
        - Test availability via webping
        - Test availability via connect
        - Parameters
        
### USER GUIDE
- Troubleshooting
    - Diagnostic & Debug Logs


---
### OVERVIEW

#### About the TA-connectivity

| Author | Oluwaseun Remi-Omosowon |
| --- | --- |
| App Version | 1.0 |
| Vendor Products | <ul><li>SDK for Python 1.6.0</li></ul> |

The TA-connectivity app can be used to gather host connectivity information. 
It leverages the multiprocessing library in python using a pool of 4 workers. 
It contains 3 different scripts namely; ping.py, webping.py and connect.py
Available at:

[Splunkbase](https://splunkbase.splunk.com/app/1473/#/details)

[Github](https://github.com/seunomosowon/TA-connectivity)

**Note:** This is not backward compatibile with releases before v0.4.

This app adds 3 modular inputs to any Splunk installation:
1. ping://
2. webping://
3. connect://

This also allows the specification of of how many threads should be used to handle a the provided list of hosts.

##### Scripts and binaries

Includes:
- Splunk SDK for Python (1.6.0)
- mail_lib - supports the calculation of vincenty distances which is used by default
    - ping.py - Tests connectivity using ICMP to multiple systems
    - webping - tests connectivity to mulyiple web application given the application URLs
    - connect - Checks TCP connectivity to a given socket (hostname and port)
    - connectivity_lib - library with exception handling, constants, and utility functions used for actually 
      connecting to hosts. 
        - connect_test.py   - function for testing connectivity to a TCP socket
        - constants.py      - contains constants used throughout the library
        - exceptions.py     - contains exceptions for ping / webping and connect modular inputs
        - pinger.py         - functions for pinging hosts from windows or unix systems.
        - webtest.py        - contains functions to test connectivity to websites.

#### Release notes

##### About this release
Version 1.0 of the TA-connectivity is compatible with:

| Splunk Enterprise versions | 6.x |
| --- | --- |
| CIM | Not Applicable |
| Platforms | Platform independent |
| Lookup file changes | No lookups included in this app |

This includes definitions for 3 sourcetypes listed below which use common fields such as action, status, src and url.
- ping
- webping
- connect

This app will not work on a universal forwarder, 
as it requires Python which comes with an HF or a full Splunk install.

##### New features

TA-connectivity v1.0 includes the following new features:

- Improved documentation
- Added configuration to allow automated tests of all modular inputs added by this TA via [Travis CI](http://travis-ci.org/)  
- Removed interval from inputs.conf.spec to pass appinspection
- Fixed exception handling for connect where connection is refused
- Refactored code to reduce imports all over the place.

##### Known issues

Currently no known issues in version 1.0 of TA-connectivity. 
Issues can be reported on Splunkbase or Github at this time.


##### Third-party software attributions

This uses libraries freely available in python.

Contributions on github are welcome and will be incorporated into the main release. 
Current contributors are listed in AUTHORS.md.

#### Support and resources

**Questions and answers**

Access questions and answers specific to the TA-connectivity at (https://answers.splunk.com/).

**Support**

This Splunk support add-on is community / developer supported.

Questions asked on Splunk answers will be answered either by the community of users or by the developer when available.
All support questions should include the version of Splunk and OS.

You can also contact the developer directly via [Splunkbase](https://splunkbase.splunk.com/app/1473/).
Feedback and feature requests can also be sent via Splunkbase.

Issues can also be submitted at the [TA-connectivity repo via on Github](https://github.com/seunomosowon/TA-connectivity/issues)

##### Older Releases

- v0.4.8
* Fixed bug with pinger script for windows

- v0.4.7
* Updated regex extractions to parse more pinger script.
* Removed ping limitations for linux and windows. (would expose the variables in next release)
* Rewrote parts of the ping script -
* Added some disabled inputs for windows

Some of the updates to v0.4.7 came from user feedback.

## INSTALLATION AND CONFIGURATION
### Hardware and software requirements

#### Hardware requirements

TA-connectivity supports the following server platforms in the versions supported by Splunk Enterprise:

- Linux
- Windows

**Note** :  While this has been written to be platform independent,  please report any issues found with using this 
technology add-on in a windows environment. 

Automated tests have been setup to confirm all functions of this TA following an update to the code.

Please contact the developer with issues running this on Windows. See the Splunk documentation for hardware 
requirements for running a heavy forwarder. 

#### Software requirements

To function properly, TA-connectivity has no external requirements but needs to be installed on a full Splunk 
install which includes a limited version of python.

#### Splunk Enterprise system requirements

Because this add-on runs on Splunk Enterprise, all of the [Splunk Enterprise system requirements](http://docs.splunk.com/Documentation/Splunk/latest/Installation/Systemrequirements) apply.

### Installation steps

Download the TA-connectivity at one of the following locaitons:
- [Splunkbase](https://splunkbase.splunk.com/app/1473/#/details)
- [Github](https://github.com/seunomosowon/TA-connectivity)
 

##### Deploy to single server instance

To install and configure this app on your supported standalone platform, do one of the following:

- Install on a standalone Splunk Enterprise install via the GUI. [See Link](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall)
- Extract the technology add-on to ```$SPLUNK_HOME/etc/apps/``` and restart Splunk

##### Deploy to distributed deployment

**Install to search head** - (Standalone or Search head cluster)

- Install the support add-on located at ```TA-connectivity/appserver/SA-mailclient.tgz``` on the search head.
If using search head cluster, install the SA-mailclient.tgz via a search head deployer.

**Install to indexers**

- No App needs to be installed on indexers

**Install to forwarders**

- Follow the steps to install the TA-connectivity on a heavy forwarder.
More instructions available at the following [URL](https://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall#Heavy_forwarders)

- Configure an email input by going to the setup page or configuring inputs.conf.

##### Deploy to Splunk Cloud

For Splunk cloud installations, install TA-connectivity on a heavy forwarder that has been configured to forward 
events to your Splunk Cloud instance. 

You can work with Splunk Support on installing the Support add-on on Splunk Cloud.


#### Configure TA-connectivity

A list of hosts must be provided in the form of a lookup.
This requires a "url" field for testing webconnectivity using the webping modular input.

For ping and connect modular inputs, this expects a field for hostname and port .
If port field is not specified, it expects the host_field to be in the format *hostname:port* or *IP:port*.


*Sample CSV:*
```csv
hostname,port,url
www.google.com,80,https://encrypted.google.com
www.yahoo.com,80,http://www.yahoo.com
4.2.2.2,53,http://www.twitter.com
8.8.8.8,53,http://www.linkedin.com
```

*Sample CSV2:*
```csv
socket
www.google.com:80
www.yahoo.com:80
4.2.2.2:53
8.8.8.8:53
```


##### Test availability via Ping.

This input extracts hostnames or IP addreses from the host_field header column of the csv defined by the input.
If workers is not defined, it uses a default of 4 workers.

*Example 1*
```
[ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt]
host_field = hostname
workers = 4
interval = 600
```

*Test 1: Testing the ping modular input above*
```
/opt/splunk/bin/splunk cmd splunkd print-modinput-config ping ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt | /opt/splunk/bin/splunk cmd python /opt/splunk/etc/apps/TA-connectivity/bin/ping.py
```

*Output of Test1:*
```xml
<stream>
    <event stanza="ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
        <data>
            06/23/2016 12:38:44 BST ,action=ping succeeded,status=200,src=splunk,dst_hostname=www.google.com,dst_ip=216.58.198.164,description="icmp_seq=1 ttl=55;icmp_seq=2 ttl=55",average_rtt=101.5,packet_loss=0%
        </data>
        <done />
    </event>
    <event stanza="ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
        <data>
            06/23/2016 12:38:44 BST ,action=ping succeeded,status=200,src=splunk,dst_hostname=www.yahoo.com,dst_ip=46.228.47.114,description="icmp_seq=1 ttl=54;icmp_seq=2 ttl=54",average_rtt=105.5,packet_loss=0%
        </data>
        <done />
    </event>
    <event stanza="ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
        <data>
            06/23/2016 12:38:44 BST ,action=ping succeeded,status=200,src=splunk,dst_hostname=4.2.2.2,dst_ip=4.2.2.2,description="icmp_seq=1 ttl=58;icmp_seq=2 ttl=58",average_rtt=101.5,packet_loss=0%
        </data>
        <done />
    </event>
    <event stanza="ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
        <data>
            06/23/2016 12:38:44 BST ,action=ping succeeded,status=200,src=splunk,dst_hostname=8.8.8.8,dst_ip=8.8.8.8,description="icmp_seq=1 ttl=55;icmp_seq=2 ttl=55",average_rtt=101.0,packet_loss=0%
        </data>
        <done />
    </event>
</stream>
```

##### Test availability via webping
The following input configuration would test web connectivity to all hosts in the csv using the URLs stored in the "host" column
The modular input uses a default of 4 workers when not configured, and a web timeout of 5s.

*Example 2*
```
[webping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt]
host_field = hostname
workers = 4
web_timeout = 5
interval = 600
```

*Test 2: WebPing modular input*
```
/opt/splunk/bin/splunk cmd splunkd print-modinput-config webping webping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt | /opt/splunk/bin/splunk cmd python /opt/splunk/etc/apps/TA-connectivity/bin/webping.py
```

*Output of command:*
```xml
    <stream>
        <event stanza="webping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 03:54:35 BST,action=successful,status=200,src=splunk,dst=encrypted.google.com,url="https://encrypted.google.com",description=online</data>
            <done />
        </event>
        <event stanza="webping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 03:54:35 BST,action=successful,status=200,src=splunk,dst=www.yahoo.com,url="http://www.yahoo.com",description=online</data>
            <done />
        </event>
        <event stanza="webping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 03:54:35 BST,action=successful,status=200,src=splunk,dst=www.twitter.com,url="http://www.twitter.com",description=online</data>
            <done />
        </event>
        <event stanza="webping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 03:54:35 BST,action=successful,status=200,src=splunk,dst=www.linkedin.com,url="http://www.linkedin.com",description=online</data>
            <done />
        </event>
    </stream>
```

##### Test availability via connect
This tests the connection to a host on a specified port.
If port\_field is not specified, it expects the host\_field to be in the format *hostname:port* or *IP:port*.

*Example 3*
```
[connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt]
host_field = hostname
port_field = port
workers = 5
interval = 600
```

*Example 4*
```
[connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile2.txt]
host_field = socket
workers = 4
interval = 600
disabled=true
```

Test 3: Connect modular input
```
/opt/splunk/bin/splunk cmd splunkd print-modinput-config connect connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt | /opt/splunk/bin/splunk cmd python /opt/splunk/etc/apps/TA-connectivity/bin/connect.py
```

*Output of command:*
```xml
    <stream>
        <event stanza="connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 04:44:49 BST ,action=connection succeeded,status=200,src=splunk,dst_hostname=www.google.com,dst_ip=216.58.210.36,description=Connection successful to host=www.google.com on port=80
            </data>
            <done />
        </event>
        <event stanza="connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 04:44:49 BST ,action=connection succeeded,status=200,src=splunk,dst_hostname=www.yahoo.com,dst_ip=46.228.47.115,description=Connection successful to host=www.yahoo.com on port=80
            </data>
            <done />
        </event>
        <event stanza="connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 04:44:49 BST ,action=connection succeeded,status=200,src=splunk,dst_hostname=4.2.2.2,dst_ip=4.2.2.2,description=Connection successful to host=4.2.2.2 on port=53
            </data>
            <done />
        </event>
        <event stanza="connect:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt" unbroken="1">
            <data>
                06/19/2016 04:44:49 BST ,action=connection succeeded,status=200,src=splunk,dst_hostname=8.8.8.8,dst_ip=8.8.8.8,description=Connection successful to host=8.8.8.8 on port=53
            </data>
            <done />
        </event>
    </stream>
```


##### Parameters

- \[ping:///path/to/lookup\]

    **host_field** - This identifies the column name in the csv that will contain host names to be pinged.
    This can be in the form of hostname:port or ip:port when using connect, without specifying a port_field 

    **workers** - This is an optional parameter which specifies how many worker processes should be used for a specific 
    instance of this modular input.

- \[webping:///path/to/lookup\]

    **host_field** - This identifies the column name in the csv that will contain host names to be tested.
    This must be in the form of a URL with a scheme - https://hostname:port. 

    **workers** - This is an optional parameter which specifies how many worker processes should be used for a specific 
    instance of this modular input.

    **web_timeout** - This defines the web timeout to be used for the availability tests.

- \[connect:///path/to/lookup\]

    **host_field** - This identifies the column name in the csv that will contain host names to be pinged.
    This can be in the form of hostname:port or ip:port when using connect, without specifying a port_field 

    **workers** - This is an optional parameter which specifies how many worker processes should be used for a specific 
    instance of this modular input.

    **port_field**
    This marks the column name in the csv that will contain destination ports to be used for this test.
    If it is not specified, then the connect modular input expects the hostname in the form hostname:port or IP:port.


## USER GUIDE

### Troubleshooting

This can be tested as demonstrated above by using the following command syntax:
```
/opt/splunk/bin/splunk cmd splunkd print-modinput-config ping ping:///opt/splunk/etc/apps/TA-connectivity/lookups/hostfile.txt | /opt/splunk/bin/splunk cmd python /opt/splunk/etc/apps/TA-connectivity/bin/ping.py
```

#### Diagnostic & Debug Logs

Logs can be found by searching Splunk internal logs
 
```index=_internal sourcetype=splunkd (component=ModularInputs OR component=ExecProcessor) (connect.py OR ping.py OR webping.py)```


Additional logging can be enabled by turning on debug logging for ExecProcessor and ModInputs.
set the logging level of the ExecProcessor to Debug

/opt/splunk/bin/splunk set log-level ExecProcessor -level DEBUG
/opt/splunk/bin/splunk set log-level ModInputs -level DEBUG

You can find additional ways to enable debug logging on 
[here](http://docs.splunk.com/Documentation/Splunk/latest/Troubleshooting/Enabledebuglogging).
