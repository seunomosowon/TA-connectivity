"""
This includes functions to be used for web connectivity tests to a given URL.
Functions here support the 'webping://' modular input
"""

from future.standard_library import install_aliases
install_aliases()
import re
from urllib.request import urlopen
from urllib.parse import urlparse
from http.client import HTTPException
import urllib.error
from time import strftime
from string import Template


""" 
Still need to capture traceback and log to debug?
import traceback 
"""

logmessage = Template(
    '$timenow,action=$action,status=$status_code,src=splunk,dst=$dsthost,url=\"$dsturl\",description=$description')


def webtest(url, webtimeout):
    """
    This tests connectivity to a webservice running at a given URL.
    :param url: Application URL to be tested.
    :type url: basestring
    :param webtimeout: application web timeout to be used for the test.
    :type webtimeout: int
    :return: Raises an exception or returns a status message about the connection tested
    :rtype: basestring
    """
    timenow = strftime("%m/%d/%Y %H:%M:%S %Z")
    dst = urlparse(url).netloc.split(':')[0]
    # raise exception if url is not in format required or return as unsuccessful
    action = ''
    description = ''
    try:
        openurl = urlopen(url, timeout=webtimeout)
        status_code = openurl.getcode()
        if re.match('(2\d\d)', repr(status_code)):
            if re.match('(2\d\d)', repr(status_code)):
                action = 'successful'
                description = 'online'
        elif re.match('(3\d\d)', repr(status_code)):
            action = 'redirected'  # These falls under urllib2.HTTPError
            description = 'redirected'
        elif re.match('(4\d\d)', repr(status_code)):
            action = 'unsuccessful'
            description = 'Malformed URL'
        elif re.match('(5\d\d)', repr(status_code)):
            action = 'unsuccessful'
            description = 'Server Error'
        else:
            action = 'unknown'
            description = 'unknown'
    except urllib.error.HTTPError as e:
        action = 'HTTPERROR'
        description = 'HTTPError - ' + repr(e. code)
        status_code = e.code
    except urllib.error.URLError as e:
        action = 'URLERROR'
        description = 'URLError - ' + str(e.reason)
        status_code = 999
    except HTTPException:
        action = 'PROGRAM_ERROR'
        description = 'HTTPException'
        status_code = 999
    return logmessage.substitute(
        timenow=timenow, action=action, status_code=status_code, dsthost=dst, dsturl=url, description=description)
