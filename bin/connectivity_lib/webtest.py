import re
#import traceback
from string import Template
from time import strftime
import urllib2
urlparse=urllib2.urlparse.urlparse
from httplib import HTTPException

logmessage = Template('$timenow,action=$action,status=$status_code,src=splunk,dst=$dsthost,url=\"$dsturl\",description=$description')

def webtest(url,webtimeout):
    """
    This tests connectivity to a webservice running at a given URL.
    :param url: Application URL to be tested.
    :type basestring
    :param webtimeout: application web timeout to be used for the test.
    :return: Raises an exception or returns a status message about the connection tested
    :rtype: basestring
    """
    timenow = strftime("%m/%d/%Y %H:%M:%S %Z")
    dst = urlparse(url).netloc.split(':')[0]
    # raise exception if url is not in format required or return as unsuccessful
    action=''
    description=''
    try:
        openurl = urllib2.urlopen(url, timeout=webtimeout)
        status_code = openurl.getcode()
        if re.match('(2\d\d)', repr(status_code)):
            if re.match('(2\d\d)', repr(status_code)):
                action= 'successful'
                description= 'online'
        elif re.match('(3\d\d)',repr( status_code)):
            action= 'redirected'  # These falls under urllib2.HTTPError
            description= 'redirected'
        elif re.match('(4\d\d)' , repr(status_code)):
            action= 'unsuccessful'
            description= 'Malformed URL'
        elif re.match('(5\d\d)' , repr(status_code)):
            action= 'unsuccessful'
            description= 'Server Error'
        else:
            action='unknown'
            description='unknown'
    except urllib2.HTTPError, e:
        action= 'HTTPERROR'
        description = 'HTTPError - '+ repr(e. code)
        status_code=e.code
    except urllib2.URLError, e:
        action='URLERROR'
        description ='URLError - '+ str(e.reason)
        status_code=999
    except HTTPException, e:
        action='PROGRAM_ERROR'
        description ='HTTPException'
        status_code=999
    return logmessage.substitute(timenow=timenow,action=action, status_code= status_code,dsthost=dst,dsturl= url, description=
                                 description)
