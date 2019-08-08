import os
import app
import sys
import json
import time
import threading
import subprocess

def main():
    config = app.config()

    if config.system_machine in config.system_machine_using_redsocks:
        if os.getuid() != 0:
            app.log('Please run "sudo -s" first!\n', color='[R1]')
            return

    config.load()

    app.log('SOCKS5 Proxy Rotator running on port {}'.format(config.proxyrotator_port))
    app.log('Domain Fronting running on port {}'.format(config.domainfronting_port))

    app.proxyrotator(('0.0.0.0', config.proxyrotator_port), buffer_size=65535).start()

    redsocks = app.redsocks(config.is_system_machine_using_redsocks())
    redsocks.start()
    
    for i in range(int(config.core)):
        port = 3081 + i
        app.proxies.append(['127.0.0.1', port])
        app.psiphon('storage/psiphon/psiphon-tunnel-core -config storage/psiphon/{port}/config.json', port, config.kuota_data_limit).start()

    try:
        domainfronting = app.domainfronting(('127.0.0.1', config.domainfronting_port), app.domainfronting_handler)
        domainfronting.whitelist_requests = config.whitelist_requests
        domainfronting.frontend_domains = config.frontend_domains
        domainfronting.buffer_size = 65535
        domainfronting.redsocks = redsocks
        domainfronting.serve_forever()
    except OSError:
        app.psiphon_stop.append(1)
        redsocks.stop()
        app.log('Port {} used by another programs', color='[R1]'.format(config.domainfronting_port))
        app.log('Ctrl-C to exit')
    except KeyboardInterrupt:
        app.psiphon_stop.append(1)
        redsocks.stop()
        with app.lock:
            sys.stdout.write('      \r')
            sys.stdout.flush()
            app.log('Ctrl-C again to exit')

if __name__ == '__main__':
    main()
