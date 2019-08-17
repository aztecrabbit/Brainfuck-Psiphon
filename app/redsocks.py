import os
import subprocess
from .important import *

class redsocks(object):
    def __init__(self, system_machine_using_redsocks):
        super(redsocks, self).__init__()

        self._stop = False if system_machine_using_redsocks else True

    def start(self):
        if self._stop: return

        redsocks_config = \
        '''
echo '

base {
    log_debug = off;
    log_info = off;
    log = "file:/var/log/redsocks.log";
    daemon = on;
    redirector = iptables;
}

redsocks {
    local_ip = 127.0.0.1;
    local_port = 3070;

    ip = 127.0.0.1;
    port = 3080;
    type = socks5;
    login = "aztecrabbit";
    password = "aztecrabbit";
}

// Auto generated from Brainfuck Tunnel Psiphon Version
// (c) 2019 Aztec Rabbit.

' > /etc/redsocks.conf
        '''.strip()

        commands = \
        '''
redsocks
iptables -t nat -N REDSOCKS
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 3070
iptables -t nat -A OUTPUT -p tcp -j REDSOCKS
        '''.strip().replace('\r', '').replace('\n', ';').split(';')

        self.stop()

        os.system('touch /var/log/redsocks.log')
        os.system('rm /var/log/redsocks.log')
        os.system(redsocks_config)

        for command in commands:
            process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.communicate()

    def stop(self):
        if self._stop: return

        commands = \
        '''
iptables -F
iptables -X 
iptables -Z
iptables -t nat -F
iptables -t nat -X
iptables -t nat -Z
killall redsocks
        '''.strip().replace('\r', '').replace('\n', ';').split(';')

        for command in commands:
            process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.communicate()

    def update(self, hostname = ''):
        if self._stop: return
        if len(hostname) == 0: return
        with lock:
            command = 'iptables -t nat -C REDSOCKS -d {} -j RETURN'.format(hostname)
            process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                command = 'iptables -t nat -I REDSOCKS -d {} -j RETURN'.format(hostname)
                process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                process.communicate()
