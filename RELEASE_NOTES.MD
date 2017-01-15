# TA-connectivity


The TA-connectivity app can be used to gather host connectivity information. It leverages the multiprocessing library in python using a pool of 4 workers. It contains 3 different scripts namely; ping.py, webping.py and connect.py

Available at:

[Splunkbase](https://splunkbase.splunk.com/app/1473/#/details)

[Github](https://github.com/seunomosowon/TA-connectivity)

###v0.4.7
* Updated regex extractions to parse more pinger  script.
* Removed ping limitations for linux and windows. (would expose the variables in next release)
* Rewrote parts of the ping script -
* Added some disabled inputs for windows

Some of the updates to v0.4.7 came from user feedback, with code from devcompl [https://github.com/devcompl]
