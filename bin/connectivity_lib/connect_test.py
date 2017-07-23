"""
This includes functions to be used for tcp connectivity tests to a host and destination port.
Functions here support the connect:// modular input
"""

import errno
import socket
from string import Template
from time import strftime
from .exceptions import *
from .constants import *

eventmessage = Template('$timenow ,action=$action,status=$status_code,src=splunk,dst_hostname=$dsthost,'
                        'dst_ip=$dstip,description=$description')


def connect_test(dstaddr, port):
    """
    This tests connectivity to a service running on a given host and port.
    :param dstaddr: Hostname or IP address running the application being tested.
    :type dstaddr: basestring
    :param port: Port to be tested.
    :return: Raises an exception or returns a status message about the connection tested
    :rtype: basestring
    """
    timenow = strftime("%m/%d/%Y %H:%M:%S %Z")
    try:
        port = int(port)
    except ValueError:
        raise ConnectivityPortValueError(port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # new TCP socket
    except socket.error:
        raise ConnectivitySocketCreation
    dst_ip = ''
    trailer = ''
    try:
        s.connect((dstaddr, port))  # a=s.connect_ex()
        dst_ip, dst_port = s.getpeername()
        # src_ip,src_port = s.getsockname()  don't need yet..
        s.shutdown(socket.SHUT_RDWR)
        action = 'connection succeeded'
        description = "Connection successful to host=%s on port=%s" % (dstaddr, port)
        status = 200
    except socket.gaierror:
        raise ConnectivityNameResolution(dst_ip)
    except socket.error, e:
        if e.errno == errno.ECONNREFUSED:
            description = "Connection actively refused by host=%s on port=%s" % (dstaddr, port)
            action = "connection failed"
            status = 999
        else:
            raise ConnectivityNetworkError(e)
    return eventmessage.substitute(
        timenow=timenow, action=action, dsthost=dstaddr,
        dstip=dst_ip, status_code=status, description=description+trailer)
