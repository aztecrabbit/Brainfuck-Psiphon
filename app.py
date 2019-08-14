import app
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='how many core running (min 1, max 16)', dest='core', type=int)
    parser.add_argument('-r', help='reset exported files (all, config, data, database)', dest='reset', type=str)
    parser.add_argument('-f', help='frontend domains, example: akamai.net,akamai.net:443', dest='frontend_domains', type=str)
    parser.add_argument('-w', help='whitelist requests, example: akamai.net,akamai.net:443', dest='whitelist_requests', type=str)
    arguments = parser.parse_args()

    app.banners()

    config = app.config()

    if arguments.reset is not None:
        app.log('Resetting Exported Files')
        config.reset(arguments.reset)
        app.log('Resetting Exported Files Complete\n'.format(arguments.reset))
        return

    if config.system_machine not in config.files_psiphon_tunnel_core:
        app.log('This machine ({}) not available at this time!\n'.format(config.system_machine), color='[R1]')
        return

    if config.system_machine in config.system_machine_using_redsocks and not config.user_is_superuser():
        app.log('Please run "sudo -s" first! (don\'t use "sudo python3 app.py"!)\n', color='[R1]')
        return

    config.load()

    if config.force_use_redsocks and not config.user_is_superuser():
        app.log('Please run "sudo -s" first! (don\'t use "sudo python3 app.py"!)\n', color='[R1]')
        return

    if arguments.whitelist_requests is not None:
        config.whitelist_requests = app.process_to_host_port(arguments.whitelist_requests.split(','))
        arguments.whitelist_requests = ''
        for host_port in config.whitelist_requests:
            arguments.whitelist_requests += ' {}:{},'.format(host_port[0], host_port[1])
        app.log('Whitelist Requests is set by arguments: {}'.format(arguments.whitelist_requests.strip().rstrip(',')))

    if arguments.frontend_domains is not None:
        config.frontend_domains = app.process_to_host_port(arguments.frontend_domains.split(','))
        arguments.frontend_domains = ''
        for host_port in config.frontend_domains:
            arguments.frontend_domains += ' {}:{},'.format(host_port[0], host_port[1])
        app.log('Frontend Domains is set by arguments: {}'.format(arguments.frontend_domains.strip().rstrip(',')))

    app.log('SOCKS5 Proxy Rotator running on port {}'.format(config.proxyrotator_port))
    app.log('Domain Fronting running on port {}'.format(config.domainfronting_port))

    app.proxyrotator(('0.0.0.0', config.proxyrotator_port), buffer_size=65535).start()

    redsocks = app.redsocks(config.is_redsocks_enabled())
    redsocks.start()
    
    for i in range(int(arguments.core if arguments.core is not None and arguments.core > 0 and arguments.core <= 16 else config.core)):
        port = 3081 + i
        app.proxies.append(['127.0.0.1', port])
        app.psiphon(
            '{} -config storage/psiphon/{}/{}'.format(app.real_path(config.files_psiphon_tunnel_core[config.system_machine][1]), port, 'config-multi-tunnel.json' if config.is_multi_tunnel_enabled() else 'config.json'),
            port, config.kuota_data_limit, config.is_multi_tunnel_enabled()
        ).start()

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
            app.log('Ctrl-C again to exit    ')

if __name__ == '__main__':
    main()
