#!/usr/bin/python

import SimpleHTTPServer
import BaseHTTPServer
import socket
import ssl

__version__ = "0.1"


class StatusServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    server_version = "StatusServer" + __version__
    timeout = 0.5

    def do_GET(self):
        echostring = '%s %s %s\r\n' % (self.command, self.path, self.request_version)
        for k in self.headers.keys():
            echostring += "%s: %s\r\n" % (k, self.headers[k])
        try:
            echostring += self.rfile.read()
        except Exception, e:
            print e.message, "no http entity received"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(len(echostring)))
        self.end_headers()
        self.wfile.write(echostring)

if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', 4433), StatusServerHandler)
    httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                   keyfile='/etc/nginx/ssl/nginx.key',
                                   certfile='/etc/nginx/ssl/nginx.crt',
                                   server_side=True)
    httpd.serve_forever()

