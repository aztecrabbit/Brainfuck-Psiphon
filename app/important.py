import os
import re
import subprocess
from threading import RLock

lock = RLock()
proxies = []
psiphon_stop = []
regex_host_port = r'([^/:]+(\.[^/:]+)?)(:([0-9*]+))?'

def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def xfilter(data):
    for i in range(len(data)):
        data[i] = data[i].strip()
        if data[i].startswith('#'):
            data[i] = ''

    return [x for x in data if x]

def process_to_host_port(data_list):
    data_list = xfilter(data_list)
    data = []

    for temp in data_list:
        temp = re.findall(regex_host_port, temp)[0]
        host = temp[0]
        port = temp[3] if len(temp) >= 4 and len(temp[3]) else '80'

        if host and port: data.append([host, port])

    return data