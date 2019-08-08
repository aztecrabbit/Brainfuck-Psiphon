import re
import socket
import select
import random
import socketserver
from .redsocks import *
from .important import *

class domainfronting(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class domainfronting_handler(socketserver.BaseRequestHandler):

    def request_in_whitelist(self, socket_client_request_host, socket_client_request_port):
        if len(self.server.whitelist_requests) == 0:
            return True

        for whitelist_request in self.server.whitelist_requests:
            if (whitelist_request[0] == '*' or  whitelist_request[0] in socket_client_request_host) and \
               (whitelist_request[1] == '*' or  whitelist_request[1] == socket_client_request_port):
                return True

        return False

    def handler(self, socket_client, socket_server, buffer_size):
        sockets = [socket_client, socket_server]
        timeout = 0
        while True:
            timeout += 1
            socket_io, _, errors = select.select(sockets, [], sockets, 3)
            if errors: break
            if socket_io:
                for sock in socket_io:
                    try:
                        data = sock.recv(buffer_size)
                        if not data: break
                        # SENT -> RECEIVE
                        elif sock is socket_client:
                            socket_server.sendall(data)
                        elif sock is socket_server:
                            socket_client.sendall(data)
                        timeout = 0
                    except: break
            if timeout == 10: break

    def handle(self):
        try:
            socket_client = self.request
            socket_client_request = re.findall(r'([^/]+(\.[^/:]+)+)(:([0-9]+))?', socket_client.recv(1024).decode('charmap').split(' ')[1])[0]
            socket_client_request_host = socket_client_request[0]
            socket_client_request_port = socket_client_request[3] if len(socket_client_request) >= 4 and len(socket_client_request[3]) else '80'
        except Exception:
            self.server.close_request(self.request)
            return

        if self.request_in_whitelist(socket_client_request_host, socket_client_request_port) == False:
            self.request.sendall('HTTP/1.1 403 Forbidden\r\n\r\n'.encode())
            self.server.close_request(self.request)
            return

        try:
            frontend_domain = random.choice(self.server.frontend_domains)
            frontend_domain_host = str(frontend_domain[0])
            frontend_domain_port = int(frontend_domain[1])
        except IndexError:
            frontend_domain_host = str(socket_client_request_host)
            frontend_domain_port = int(socket_client_request_port)

        try:
            self.server.redsocks.update(frontend_domain_host)
            socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_server.connect((frontend_domain_host, frontend_domain_port))
            socket_client.sendall('HTTP/1.1 200 OK\r\n\r\n'.encode())
            self.handler(socket_client, socket_server, self.server.buffer_size)
        except Exception:
            pass
        finally:
            self.server.close_request(self.request)
            socket_server.close()
