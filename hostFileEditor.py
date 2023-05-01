import json
import platform
import re

import requests


class Hosts():

    def __init__(self, location: str = None) -> None:

        # Init location of hosts file, grab file data and add cloudflare manually (Will need it later)
        self.os = platform.system()
        
        self.locations = {
            "Linux": "/etc/hosts",
            "Windows": "%SystemRoot%\\System32\\drivers\\etc\\hosts",
            "Darwin": "/etc/hosts"  # ? Unsure if MacOS is '/etc/hosts' or '/private/etc/hosts'
        }

        self.location = location or self.locations[self.os]
        self.data = self.read_data()
        self.set_host('cloudflare-dns.com', '104.16.248.249')

        # Reset Info
        self.windows_hosts = """
# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
# localhost name resolution is handled within DNS itself.
# 102.54.94.97    rhino.acme.com                   # source server
# 38.25.63.10     x.acme.com                       # x client host
# 127.0.0.1       localhost
# ::1             localhost
"""

        self.macos_hosts = """
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting. Do not change this entry.
##
127.0.0.1 localhost
255.255.255.255 broadcasthost
::1 localhost
fe80::1%lo0 localhost
"""

        self.linux_hosts = f"""
127.0.0.1       localhost {platform.node()}
::1             localhost ip6-localhost ip6-loopback
fe00::0         ip6-localnet
ff00::0         ip6-mcastprefix
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
"""

        return

    def __repr__(self) -> str:
        """
        Print Obj return
        """
        return f"Hosts file {self.location}"

    def set_host(self, url: str, ip: str = None) -> None:
        """
        Add new URL
        """
        domain = get_domain(url)

        try:
            if ip:
                self.data[domain] = ip
            else:
                self.data[domain] = get_ip(self.get_domain(url))

            self.save()
        except Exception as e:
            print(e)

    def add(self, url: str, ip: str = None):
        """
        Add a new URL
        """
        self.set_host(url, ip)

    def save(self):
        """
        Save the new file
        """
        with open(self.location, 'w') as f:
            f.writelines("%s %s\n" % (self.data[key], key)
                         for key in list(self.data.keys()))
        return

    def read_data(self) -> dict:
        '''
        Read data from hosts file and

        convert it to a dictionary.
        '''
        with open(self.location, 'r') as f:
            return self.format_host_to_dict(f.readlines())

    def format_host_to_dict(self, text: list) -> dict:
        '''
        Convert from

        <ip> <location>

        to

        {<location>:<ip>}
        '''
        host_dict = dict()

        for line in text:
            # Skip comment lines
            if line.startswith('#'):
                continue
            # Remove double spaces
            while '  ' in line:
                line = line.replace('  ', ' ')
            if line.strip() == "":
                continue
            ip, *urls = line.split()
            # Add each URL to the dict
            for url in urls:
                host_dict[url.strip()] = ip.strip()
        if len(host_dict) > 2:
            return host_dict
        else:
            raise ValueError("Less than 2 Keys - Something went wrong?")

    def reset(self):
        """
        Reset host file
        """
        default_host = None

        match self.os:
            case "Linux":
                default_host = self.linux_hosts
            case "Windows":
                default_host = self.windows_hosts
            case "Darwin":
                default_host = self.macos_hosts
            case _:
                raise TypeError("Unsure what OS You're running...")

        with open(self.location, 'w') as f:
            f.write(default_host)
        return

def get_ip(domain: str) -> str:
    """
    Get IP from domain"""

    response = json.loads(
        requests.post(
            f"https://cloudflare-dns.com/dns-query?name={domain}", headers={"Content-Type": "application/dns-json"}
        ).text
    )
    match response['Status']:
        case 0:
            pass
        case 1:
            raise Exception("Format Error")
        case 2:
            raise Exception("Server Failure")
        case 3:
            raise Exception("Non-Existent Domain")
        case 5:
            raise Exception("Query Refused")
        case _:
            raise Exception(
                f"Error raised: Status {response['Status']}, see https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6 for more info")

    for i in response['Answer']:
        if i['type'] == 1:
            ip = i['data']
            print(f"{domain}: {ip}\nAdded!")
            break

    if ':' in ip or '.' in ip:
        return ip
    else:
        raise Exception("Could not find IP")

def get_domain(url: str) -> str:
    """
    Get domain from URL

    (https://google.com -> google.com)
    """
    domain_regex = re.compile(
        r"^\s*(?:https?:\/\/)?(?:[^@\/\n]+@)?(?P<domain>[^:\/?\\\s]+\.[^:\/?\\\s]+)")
    matches = domain_regex.search(url)
    if matches == None:
        return None
    domain = matches.group("domain")
    return domain