"""
This includes functions to be used for ICMP echo (ping) tests to a host and destination.
Functions here support the 'ping://' modular input
"""

import re
import platform
#import traceback
from string import Template
from subprocess import PIPE
from subprocess import Popen as popen
from time import strftime


eventmsg = Template('$timenow ,action=$action,status=$status_code,src=splunk,dst_hostname=$dsthost,dst_ip=$dstip,description=$description')
regex_ip = r'(?P<ip_address>(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
regex_hostname = r"(?P<hostname>((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])+))"
regex_hostname_ip = "%s(?:\s\(%s\))?" % (regex_hostname,regex_ip)
regex_ttl = r'.*TTL=(?P<ttl>\d+)'


def pingtest(dstaddr):
    timenow = strftime("%m/%d/%Y %H:%M:%S %Z")
    dstaddr = dstaddr.rstrip('\r\n')
    trailer = ''
    action=''
    description=''
    dst_ip=''
    status=''
    if platform.system() == 'Windows':
        p = popen(['ping', '-n', '2', '-l', '1', str(dstaddr)], stdout=PIPE, stderr=PIPE)
        if p:
            """command was successful"""
            output, err = p.communicate()
            pattern_ping_request = r'^Pinging[\s](?:%s\s)*\[?%s\]?' % (regex_hostname, regex_ip)
            pattern_ping_reply = r'^Reply\sfrom\s%s.*$' % regex_ip
            pattern_rtt = r'Average = (?P<rtt>\d+ms)'
            pattern_loss = r'Lost\s=\s\d+\s\((?P<packet_loss>\d+%).*$'
            request_regex = re.search(pattern_ping_request, output,
                                      re.M)
            # I think this will always match except if IP unresolved in which case p=false - Investigate
            if request_regex:
                dst_ip = request_regex.group('ip_address')
                reply_regex = re.search(pattern_ping_reply, output, re.M)
                if reply_regex:
                    reply_ip = reply_regex.group('ip_address')
                    pattern_description = r'Reply\sfrom.*:\s(?P<description>.*)[\r\n]'
                    if reply_ip == dst_ip:
                        action = 'ping succeeded'
                        status = 200
                        # ttl = reply_regex.group('ttl')
                        rex_rtt = re.search(pattern_rtt, output, re.M)
                        if rex_rtt:
                            rtt = rex_rtt.group('rtt')
                            trailer = trailer + ',average_rtt=' + rtt
                    else:
                        action = 'ping failed'
                        status = 998
                    rex_description = re.findall(pattern_description, output,re.M)
                    # matches "reply from w.x.y.z: destination host unreachable"
                    if rex_description:
                        description = '\"' + ';'.join([d for d in rex_description]) + '\"'
                else:
                    # doesn't contain "Reply from a.b.c.d"
                    pattern_description = r'Pinging.*:[\r\n](?P<ping_error>[\w\s]+)'
                    rex_description = re.findall(pattern_description, output, re.M)
                    description = re.search(r'Pinging.*:[\r\n](?P<ping_error>[\w\s]+)', output).group(
                        'ping_error')  # matches errors like "request timed out"
                    action = 'ping failed'
                    status = 998
                pcktloss_regex = re.search(pattern_loss, output, re.M)
                if pcktloss_regex:
                    packet_loss = pcktloss_regex.group('packet_loss')
                    trailer = trailer + ',packet_loss=' + packet_loss
        else:
            # error running ping command, ping command returned False return code
            status = 999
            output='' # will try get error code here p.returncode
            pattern_ping_request = r'^Pinging[\s]%s\s\[%s\]' % (regex_hostname, regex_ip)
            request_regex = re.search(pattern_ping_request, output, re.M)
            if request_regex:
                dst_ip = request_regex.group('ip_address')
                pattern_description = r'Reply\sfrom.*:\s(?P<description>[\w\s]+)$'
                rex_description = re.search(pattern_description, output, re.M)
                if rex_description:
                    description = rex_description.group('description')
            action = 'ping failed'
            if description is None:
                description = re.search(r'^\w.*$', output)
    else:
        # Linux extractions - ping -s 0 -c 2 -i 0.2 192.168.13.254
        p = popen(['ping', '-s', '1', '-c', '2', '-i', '0.2', str(dstaddr)], stdout=PIPE, stderr=PIPE)
        if p:
            # Command was launched successfully
            output, err = p.communicate()
            # print dstaddr
            if err:
                # Linux sends errors to stderr like "connect: Network is unreachable" instead of "Pinging w.x.y.x \n General failure"
                description = err
                action = 'ping failed'
                if re.match(regex_ip, dstaddr):
                    dst_ip = dstaddr
                else:
                    dst_ip = ''
                status = 999
            else:
                pattern_ping_request = r'^PING[\s]%s' % regex_hostname_ip
                pattern_ping_reply = r'^\d+\sbytes\sfrom\s%s:\s(?P<description>.*ttl=(?:\d+))$' % regex_hostname_ip
                pattern_statistics = r'^(?P<packet_no>\d+)\spackets\stransmitted,\s(?:\d+)\sreceived,\s(?P<packet_loss>\d+%)\spacket\sloss,\stime\s(?P<rtt>\d+)ms'
                request_regex = re.search(pattern_ping_request, output, re.M)
                if request_regex:
                    dst_ip = request_regex.group('ip_address')
                    if dst_ip is None:
                        dst_ip = request_regex.group('hostname')
                    reply_regex = re.search(pattern_ping_reply, output, re.M)
                    if reply_regex:
                        reply_ip = reply_regex.group('ip_address')
                        if reply_ip is None:
                            reply_ip = reply_regex.group('hostname')
                        if reply_ip == dst_ip:
                            action = 'ping succeeded'
                            status = 200
                        else:
                            action = 'ping failed'
                            status = 998
                        # matches "reply from w.x.y.z: destination host unreachable"
                        description = '\"' + ';'.join([x.group('description') for x in re.finditer(pattern_ping_reply,output,re.M)]) + '\"'
                    else:
                        action = 'ping failed'
                        status=998
                    rex_stats = re.search(pattern_statistics, output, re.M)
                    if rex_stats:
                        packet_no = rex_stats.group('packet_no')
                        packet_loss = rex_stats.group('packet_loss')
                        rtt = float(rex_stats.group('rtt')) / int(packet_no)
                        trailer = trailer + ',average_rtt=' + str(rtt) + ',packet_loss=' + packet_loss
    return eventmsg.substitute(timenow=timenow, action=action, dsthost=dstaddr, dstip=dst_ip, status_code=status,
                                     description=description + trailer)


"""
    except TypeError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** print_tb:"
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print "*** print_exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        print "*** print_exc:"
        traceback.print_exc()
        print "*** format_exc, first and last line:"
        formatted_lines = traceback.format_exc().splitlines()
        print formatted_lines[0]
        print formatted_lines[-1]
        print "*** format_exception:"
        print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print "*** extract_tb:"
        print repr(traceback.extract_tb(exc_traceback))
        print "*** format_tb:"
        print repr(traceback.format_tb(exc_traceback))
        print "*** tb_lineno:", exc_traceback.tb_lineno


UNIX_TEST_OUTPUT1="PING 8.8.8.8 (8.8.8.8) 0(28) bytes of data.\n" \
"8 bytes from 8.8.8.8: icmp_seq=1 ttl=55\n" \
"8 bytes from 8.8.8.8: icmp_seq=2 ttl=55\n" \
"\n" \
"--- 8.8.8.8 ping statistics ---\n" \
"2 packets transmitted, 2 received, 0% packet loss, time 202ms"
UNIX_TEST_OUTPUT2="PING www.google.com (216.58.198.164) 0(28) bytes of data.\n" \
8 bytes from lhr25s10-in-f4.1e100.net (216.58.198.164): icmp_seq=1 ttl=55\n" \
8 bytes from lhr25s10-in-f4.1e100.net (216.58.198.164): icmp_seq=2 ttl=55\n" \
"\n" \
"--- www.google.com ping statistics ---\n" \
"2 packets transmitted, 2 received, 0% packet loss, time 201ms"

"""