"""
This includes functions to be used for ICMP echo (ping) tests to a host and destination.
Functions here support the 'ping://' modular input
"""


import re
import platform
from string import Template
from subprocess import PIPE
from subprocess import Popen
from time import strftime
# import traceback


class PingResult:
    """
    This class holds ping results
    """
    def __init__(self):
        self.description = '\n'
        self.trailer = '\n'
        self.action = ''
        self.dst_ip = ''
        self.status = 0


event_msg = Template('$timenow ,action=$action,status=$status_code,src=splunk,'
                     'dst_host=$dsthost,dst_ip=$dstip,description=$description')
regex_ip = (r'(?P<ip_address>(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)'
            r'{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))')
regex_hostname = (r'(?P<hostname>((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'
                  r'(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])+))')
regex_hostname_ip = r"{}(?:\s\({}\))?".format(regex_hostname, regex_ip)
regex_ttl = r'.*TTL=(?P<ttl>\d+)'


def pingtest(dest):
    timenow = strftime("%m/%d/%Y %H:%M:%S %Z")
    dest = dest.rstrip('\r\n')

    if platform.system() == 'Windows':
        result = ping_windows(dest)
    else:
        result = ping_linux(dest)
    return event_msg.substitute(timenow=timenow, dsthost=dest, action=result.action, dstip=result.dst_ip,
                                status_code=result.status,
                                description=result.description + result.trailer)


def ping_windows(dst):
    """
    :param dst: hostname or IP address to be pinged
    :return: Returns the result of a ping test
     :rtype: PingResult

    Pinging 0.0.0.0 with 32 bytes of data:
    PING: transmit failed. General failure.
    PING: transmit failed. General failure.

    Ping statistics for 0.0.0.0:
        Packets: Sent = 2, Received = 0, Lost = 2 (100% loss),

    """
    result = PingResult()
    pattern_ping_request = r'^Pinging[\s](?:{}\s)*\[?{}\]?'.format(regex_hostname, regex_ip)
    pattern_ping_reply = r'^Reply\sfrom\s(?P<ip_address>\d+.\d+.\d+.\d+):\s(?P<description>[^\r\n]+)$'
    pattern_rtt = r'Minimum\s=\s(?P<rtt_min>\d+ms),\sMaximum\s=\s(?P<rtt_max>\d+ms),\sAverage\s=\s(?P<rtt_avg>\d+ms)'
    pattern_packet_details = (r'Sent\s=\s(?P<packets_sent>\d+)\s,\sReceived\s=\s(?P<packets_received>\d+)'
                              r'\s,\sLost\s=\s(?P<packets_lost>\d+)\s\((?P<packet_loss>\d+%).*$')
    pattern_error_description = r'data:[\r\n](?:((?:PING: )?[\w \.]+)\.[\r\n])(?:((?:PING: )?[\w \.]+)\.[\r\n])'
    p = Popen(['ping', '-n', '2', str(dst)], stdout=PIPE, stderr=PIPE)
    if p:
        """command was successful"""
        output, err = p.communicate()
        if output:
            output = output.decode("utf-8")
            regex_request = re.search(pattern_ping_request, output, re.M)
            if regex_request:
                result.dst_ip = regex_request.group('ip_address')
                regex_reply = re.search(pattern_ping_reply, output, re.M)
                if regex_reply:
                    result.description += '\"' + ';'.join(
                        [x.group('description') for x in re.finditer(pattern_ping_reply, output, re.M)]) + '\"'
                    reply_ip = regex_reply.group('ip_address')
                    if reply_ip == result.dst_ip:
                        result.action = 'ping succeeded'
                        result.status = 200
                        rex_rtt = re.search(pattern_rtt, output, re.M)
                        if rex_rtt:
                            result.trailer += 'rtt_min=' + rex_rtt.group('rtt_min') + ',rtt_max=' + rex_rtt.group(
                                'rtt_max') + ',rtt_avg=' + rex_rtt.group('rtt_avg')
                    else:
                        result.action = 'ping failed'
                        result.status = 998
                else:
                    rex_description = re.findall(pattern_error_description, output)
                    result.description += '\"' + ';'.join([d for d in rex_description]) + '\"'
                    # matches errors like "request timed out" OR "PING: transmit failed. General failure."
                    result.action = 'ping failed'
                    result.status = 997
                regex_packet_details = re.search(pattern_packet_details, output, re.M)
                # Extract ping Statistics:
                # Ping statistics for 0.0.0.0:
                #     Packets: Sent = 2, Received = 0, Lost = 2 (100% loss),
                if regex_packet_details:
                    result.trailer += ',packets_sent=' + regex_packet_details.group(
                        'packets_sent') + ',packets_received=' + regex_packet_details.group(
                        'packets_received') + ',packets_lost=' + regex_packet_details.group(
                        'packets_lost') + ',packet_loss=' + regex_packet_details.group('packet_loss')
        if err:
            err = err.decode("utf-8")
            result.action = 'Ping Error'
            result.status = 996
            result.description += "Ping Error [%d] - %s" % (p.returncode, err.strip())
            result.dst_ip = dst

    else:
        # May not get here
        result.action = 'Python Popen error'
        result.status = 999
        result.description += 'Error running ping command via Popen.Make sure ping is accessible using the system PATH.'
        result.dst_ip = dst
    return result


def ping_linux(dst):
    """

    :param dst: hostname or IP address to be pinged
    :return: Returns the result of a ping test

    -bash-4.1$ ping -c 2 www.google.com
    PING www.google.com (74.125.206.147) 56(84) bytes of data.
    64 bytes from wk-in-f147.1e100.net (74.125.206.147): icmp_seq=1 ttl=49 time=7.15 ms
    64 bytes from wk-in-f147.1e100.net (74.125.206.147): icmp_seq=2 ttl=49 time=7.25 ms

    --- www.google.com ping statistics ---
    2 packets transmitted, 2 received, 0% packet loss, time 1009ms
    rtt min/avg/max/mdev = 7.153/7.205/7.257/0.052 ms
    """
    pattern_ping_request = r'^PING[\s]%s' % regex_hostname_ip
    pattern_ping_reply = r'^\d+\sbytes\sfrom\s%s:\s(?P<description>.*)$' % regex_hostname_ip
    pattern_statistics = (r'^(?P<packet_no>\d+)\spackets\stransmitted,\s(?:\d+)\sreceived,\s(?P<packet_loss>\d+)%'
                          r'\spacket\sloss,\stime\s(?P<time_taken>\d+)ms')
    pattern_rtt = (r'^rtt\smin\/avg\/max\/mdev\s=\s(?P<rtt_min>\d+\.\d+)\/(?P<rtt_avg>\d+\.\d+)'
                   r'\/(?P<rtt_max>\d+\.\d+)\/(?P<rtt_mdev>\d+\.\d+)\sms')
    result = PingResult()
    # *from previous version* - ping -s 0 -c 2 -i 0.2 192.168.13.254
    # Removed intervals and length. Makes it simpler
    p = Popen(['ping', '-c', '2', str(dst)], stdout=PIPE, stderr=PIPE)
    if p:
        # Command was launched successfully
        output, err = p.communicate()
        if err:
            err = err.decode("utf-8")
            # Linux doesn't print send error to stdout "Pinging w.x.y.x \n General failure"
            # Instead, it sends to stderr: "connect: Network is unreachable" "
            result.description += '\"' + err + '\"'
            result.status = 996
            result.action = 'ping failed'
            if re.match(regex_ip, dst):
                result.dst_ip = dst
            else:
                result.dst_ip = dst
        else:
            output = output.decode("utf-8")
            regex_request = re.search(pattern_ping_request, output, re.M)
            if regex_request:
                result.dst_ip = regex_request.group('ip_address')
                if result.dst_ip is None:
                    result.dst_ip = regex_request.group('hostname')
                regex_reply = re.search(pattern_ping_reply, output, re.M)
                if regex_reply:
                    reply_ip = regex_reply.group('ip_address')
                    if reply_ip is None:
                        reply_ip = regex_reply.group('hostname')
                    if reply_ip == result.dst_ip:
                        result.action = 'ping succeeded'
                        result.status = 200
                    else:
                        result.action = 'ping failed'
                        result.status = 998
                    # matches "reply from w.x.y.z: destination host unreachable"
                    result.description += '\"' + ';'.join(
                        [x.group('description') for x in re.finditer(pattern_ping_reply, output, re.M)]) + '\"'
                else:
                    result.action = 'ping failed'
                    result.status = 997
                rex_stats = re.search(pattern_statistics, output, re.M)
                if rex_stats:
                    # packet_no = rex_stats.group('packet_no')
                    packet_loss = rex_stats.group('packet_loss')
                    time_taken = rex_stats.group('time_taken')
                    result.trailer += '\npacket_loss=' + packet_loss + '%, time_taken=' + str(time_taken) + "ms\n"
                rex_rtt = re.search(pattern_rtt, output, re.M)
                if rex_rtt:
                    result.trailer += 'rtt_min=' + rex_rtt.group('rtt_min') + 'ms,rtt_avg=' + rex_rtt.group(
                        'rtt_avg') + 'ms,rtt_max=' + rex_rtt.group('rtt_max') + 'ms,rtt_mdev=' + rex_rtt.group(
                        'rtt_mdev') + 'ms'
    return result

