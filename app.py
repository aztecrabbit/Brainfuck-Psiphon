import os
import app
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help='how many core running (min 1, max 16)', type=int)
    arguments = parser.parse_args()
    arguments.core = 0 if arguments.core is None else arguments.core

    app.banners()

    config = app.config()

    if config.system_machine not in config.files_psiphon_tunnel_core:
        log('This machine ({}) not available at this time!'.format(config.system_machine), color='[R1]')
        return

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
    
    for i in range(int(arguments.core if arguments.core > 0 and arguments.core <= 16 else config.core)):
        port = 3081 + i
        app.proxies.append(['127.0.0.1', port])
        app.psiphon('{} -config storage/psiphon/{}/config.json'.format(app.real_path(config.files_psiphon_tunnel_core[config.system_machine][1]), port), port, config.kuota_data_limit).start()

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
        app.log('Port {} used by another programs'.format(config.domainfronting_port), color='[R1]')
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
