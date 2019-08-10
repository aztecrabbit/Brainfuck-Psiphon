import os
import time
import json
import threading
import subprocess
from .important import *
from .log import log, log_replace

class psiphon(threading.Thread):
    def __init__(self, command, port, kuota_data_limit):
        super(psiphon, self).__init__()

        self.kuota_data_limit = kuota_data_limit
        self.command = command
        self.port = port

        self.kuota_data = 0
        self.force_stop = False
        self.connected = False
        self.daemon = True

    def log(self, value, color='[G1]'):
        log(value, status=self.port, color=color)

    def log_replace(self, value, color='[G1]'):
        log_replace(value, status=self.port, color=color)

    def size(self, bytes, suffixes=['B', 'KB', 'MB', 'GB'], i=0):
        while bytes >= 1000 and i < len(suffixes) - 1:
            bytes /= 1000; i += 1

        return '{:.3f} {}'.format(bytes, suffixes[i])

    def check_kuota_data(self, received, sent):
        self.kuota_data += received + sent

        if self.kuota_data_limit > 0 and self.kuota_data >= self.kuota_data_limit:
            if sent == 0 and received <= 20000:
                return False

        return True

    def run(self):
        time.sleep(2.500)
        if len(psiphon_stop) >= 1: return        
        self.log('Connecting')
        while True:
            try:
                self.kuota_data = 0
                self.reconnecting_color = '[G1]'
                process = subprocess.Popen(self.command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in process.stdout:
                    if len(psiphon_stop) >= 1:
                        self.force_stop = True
                        break
                    line = json.loads(line.decode().strip() + '\r')
                    info = line['noticeType']
                    if info in ['Info', 'Alert']: message = line['data']['message']

                    if info == 'BytesTransferred':
                        if not self.check_kuota_data(line['data']['received'], line['data']['sent']):
                            break
                        self.log_replace(self.size(self.kuota_data))

                    elif info == 'ActiveTunnel':
                        self.connected = True
                        self.log('Connected', color='[Y1]')

                    elif info == 'Info':
                        if 'No connection could be made because the target machine actively refused it.' in message or \
                         'Memory metrics at psiphon' in message or \
                         'meek connection is closed' in message or \
                         'meek connection has closed' in message or \
                         'no such host' in message:
                            continue

                    elif info == 'Alert':
                        if 'SOCKS proxy accept error' in message:
                            if not self.connected:
                                self.reconnecting_color = '[P1]'
                                break

                        elif 'meek round trip failed' in message:
                            if self.connected: break

                        elif 'A connection attempt failed because the connected party did not properly respond after a period of time' in message or \
                         'context canceled' in message or \
                         'API request rejected' in message or \
                         'RemoteAddr returns nil' in message or \
                         'network is unreachable' in message or \
                         'close tunnel ssh error' in message or \
                         'tactics request failed' in message or \
                         'unexpected status code:' in message or \
                         'meek connection is closed' in message or \
                         'psiphon.(*MeekConn).relay' in message or \
                         'meek connection has closed' in message or \
                         'response status: 403 Forbidden' in message or \
                         'making proxy request: unexpected EOF' in message or \
                         'tunnel.dialTunnel: dialConn is not a Closer' in message or \
                         'No connection could be made because the target machine actively refused it.' in message or \
                         'no such host' in message:
                            continue

                        elif 'psiphon.(*Tunnel).sendSshKeepAlive' in message or \
                         'meek read payload failed' in message or \
                         'underlying conn is closed' in message or \
                         'psiphon.(*Tunnel).Activate' in message or \
                         'psiphon.(*Tunnel).SendAPIRequest' in message or \
                         'No address associated with hostname' in message or \
                         'controller shutdown due to component failure' in message or \
                         'tunnel failed:' in message:
                            self.reconnecting_color = '[R1]'
                            break

                        else: self.log(line, color='[R1]')
            except json.decoder.JSONDecodeError:
                self.force_stop = True
                self.log(line.decode().strip(), color='[R1]')
                self.log('Another process is running!', color='[R1]')
            except KeyboardInterrupt:
                pass
            except Exception as exception:
                self.log('Exception: {}'.format(exception), color='[R1]')
            finally:
                if self.force_stop:
                    process.kill()
                    return
                try:
                    process.kill()
                    if self.connected:
                        self.connected = False
                    self.log('Reconnecting ({})'.format(self.size(self.kuota_data)), color=self.reconnecting_color)
                except Exception as exception:
                    self.log('Stopped', color='[R1]')
                    break
