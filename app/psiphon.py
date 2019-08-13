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

        self.kuota_data = {}
        self.kuota_data_all = 0
        self.kuota_data_limit_count = 0
        self.force_stop = False
        self.daemon = True

    def log(self, value, color='[G1]'):
        log(value, status=self.port, color=color)

    def log_replace(self, value, color='[G1]'):
        log_replace(value, color=color)

    def size(self, bytes, suffixes=['B', 'KB', 'MB', 'GB'], i=0):
        while bytes >= 1000 and i < len(suffixes) - 1:
            bytes /= 1000; i += 1

        return '{:.3f} {}'.format(bytes, suffixes[i])

    def check_kuota_data(self, id, sent, received):
        if not self.kuota_data.get(id):
            self.kuota_data[id] = 0

        self.kuota_data[id] += sent + received
        self.kuota_data_all += sent + received

        limit_count = 0
        for x in self.kuota_data:
            if self.kuota_data_limit > 0 and self.kuota_data[x] >= self.kuota_data_limit:
                limit_count += 1
                if sent == 0 and received <= 20000:
                    self.kuota_data_limit_count += 1
            else: break

        if len(self.kuota_data) == limit_count or self.kuota_data_limit_count >= 7:
            return False

        return True

    def run(self):
        time.sleep(2.500)
        if len(psiphon_stop) >= 1: return        
        self.log('Connecting')
        while True:
            try:
                self.connected = 0
                self.kuota_data = {}
                self.kuota_data_all = 0
                self.reconnecting_color = '[G1]'
                self.kuota_data_limit_count = 0
                process = subprocess.Popen(self.command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in process.stdout:
                    if len(psiphon_stop) >= 1:
                        self.force_stop = True
                        break
                    line = json.loads(line.decode().strip() + '\r')
                    info = line['noticeType']
                    if info in ['Info', 'Alert']: message = line['data']['message']

                    if info == 'BytesTransferred':
                        id, sent, received = line['data']['diagnosticID'], line['data']['sent'], line['data']['received']
                        if not self.check_kuota_data(id, sent, received):
                            break
                        self.log_replace('{} ({}) ({})'.format(self.port, self.size(self.kuota_data_all), self.size(self.kuota_data[id])))

                    elif info == 'Tunnels':
                        self.connected += 1
                        if self.connected == 2:
                            self.log('Connected', color='[Y1]')

                    elif info == 'UpstreamProxyError' or \
                      info == 'ListeningSocksProxyPort' or \
                      info == 'ClientRegion' or \
                      info == 'NetworkID' or \
                      info == 'Homepage' or \
                      info == 'ServerTimestamp' or \
                      info == 'AvailableEgressRegions' or \
                      info == 'ClientUpgradeAvailable' or \
                      info == 'ActiveAuthorizationIDs':
                        continue

                    else:
                        self.log(line, color='[R1]')
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
                    self.log('Reconnecting ({})'.format(self.size(self.kuota_data_all)), color=self.reconnecting_color)
                except Exception as exception:
                    self.log('Stopped', color='[R1]')
                    break
