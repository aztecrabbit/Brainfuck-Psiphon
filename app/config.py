import os
import json
import shutil
import platform
import sysconfig
from .log import log
from .important import *

class config(object):
    def __init__(self):
        super(config, self).__init__()

        self.files_config = {
            'config': ['/data/.0000002', '/../config/config.json'],
            'frontend-domains': ['/data/.0000003', '/../config/frontend-domains.txt'],
            'whitelist-requests': ['/data/.0000004', '/../config/whitelist-requests.txt'],
        }
        self.file_psiphon_database = [
            '/data/.0000005', '/../storage/psiphon/{}/psiphon.boltdb'
        ]
        self.files_psiphon_tunnel_core = {
            'linux-x86_64': ['/data/psiphon-tunnel-core/linux-x86_64', '/../storage/psiphon/psiphon-tunnel-core'],
            'linux-armv7l': ['/data/psiphon-tunnel-core/linux-armv7l', '/../storage/psiphon/psiphon-tunnel-core'],
            'linux-armv8l': ['/data/psiphon-tunnel-core/linux-armv8l', '/../storage/psiphon/psiphon-tunnel-core'],
            'linux-aarch64': ['/data/psiphon-tunnel-core/linux-aarch64', '/../storage/psiphon/psiphon-tunnel-core'],
        }
        self.system_machine_using_redsocks = [
            'linux-x86_64'
        ]
        self.system_machine_using_multi_tunnel = [
            'linux-x86_64'
        ]

        self.system_machine = sysconfig.get_platform()
        self.system_platform = platform.system()
        self.kuota_data_limit = 4000000
        self.proxyrotator_port = 3080
        self.domainfronting_port = 8989

    def log(self, value, color='[G1]'):
        log(value, color=color)

    def user_is_superuser(self):
        return True if os.getuid() == 0 else False

    def load_config(self):
        while True:
            try:
                for x in self.files_config:
                    source, destination = [real_path(data) for data in self.files_config[x]]
                    if not os.path.exists(destination):
                        shutil.copyfile(source, destination)

                config = json.loads(open(real_path(self.files_config['config'][1])).read())
                self.core = config['core']
                self.force_use_redsocks = config['force_use_redsocks']
                self.force_use_multi_tunnel = config['force_use_multi_tunnel']
            except KeyError:
                self.log('Resetting Config to Default Settings')
                self.reset('config')
                self.log('Resetting Config to Default Settings Complete\n')
            else: break

        self.redsocks_enabled = True if self.system_machine in self.system_machine_using_redsocks or self.force_use_redsocks else False
        self.multi_tunnel_enabled = True if self.system_machine in self.system_machine_using_multi_tunnel or self.force_use_multi_tunnel else False

        self.frontend_domains = process_to_host_port(open(real_path(self.files_config['frontend-domains'][1])).readlines())
        self.whitelist_requests = process_to_host_port(open(real_path(self.files_config['whitelist-requests'][1])).readlines())

    def load_psiphon_database(self):
        source, destination = [real_path(data) for data in self.file_psiphon_database]
        for i in range(16):
            if not os.path.exists(destination.format(3081 + i)):
                shutil.copyfile(source, destination.format(3081 + i))

    def load_psiphon_tunnel_core(self):
        if self.system_machine in self.files_psiphon_tunnel_core:
            source, destination = [real_path(data) for data in self.files_psiphon_tunnel_core[self.system_machine]]
            if os.path.exists(destination):
                os.remove(destination)
            shutil.copyfile(source, destination)
            if self.system_platform == 'Linux':
                os.system('chmod +x {}'.format(destination))

    def reset(self, exported_files=''):
        exported_files = exported_files if exported_files in ['config', 'data', 'database'] else 'all'
        files = []

        if exported_files in ['all', 'config']:
            for x in self.files_config:
                files.append(self.files_config[x][1])

        if exported_files in ['all', 'data', 'database']:
            for i in range(16):
                files.append(self.file_psiphon_database[1].format(3081 + i))

            if exported_files != 'database':
                for x in self.files_psiphon_tunnel_core:
                    files.append(self.files_psiphon_tunnel_core[x][1])

        for x in files:
            try:
                os.remove(real_path(x))
            except: continue

    def load(self):
        self.load_config()
        self.load_psiphon_database()
        self.load_psiphon_tunnel_core()
