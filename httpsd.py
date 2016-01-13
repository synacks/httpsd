#!/usr/bin/python

import SimpleHTTPServer
import BaseHTTPServer
import socket
import ssl
import httplib
import urllib
import urlparse

__version__ = "0.1"


def get_token_from_dropbox(code):
    print "code: ", code, "type : ", type(code)
    params = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': 'q4nbe7oeonl0dhu',
        'client_secret': 'vf6lbqlthlul1il',
        'redirect_uri': 'https://big.xgf.ren:4433/easyspace-dropbox'
    }

    client = httplib.HTTPSConnection(host='api.dropboxapi.com', port=443, timeout=35)
    try:
        posturl = "/1/oauth2/token?" + urllib.urlencode(params)
        client.request(method="POST", url=posturl)
        print "posturl : ", posturl
        resp = client.getresponse().read()
        return resp
    except socket.timeout, e:
        print e.message
        return None


class StatusServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    server_version = "StatusServer" + __version__
    timeout = 0.5

    def do_GET(self):

        if self.path.find("easyspace") == -1:
            return

        print "deal with ", self.path

        # echostring = '%s %s %s\r\n' % (self.command, self.path, self.request_version)
        # print echostring
        # for k in self.headers.keys():
        #     echostring += "%s: %s\r\n" % (k, self.headers[k])
        #
        # try:
        #     echostring += self.rfile.read()
        # except Exception, e:
        #     print e.message, "no http entity received"

        url_components = urlparse.urlparse(self.path)
        query_dict = urlparse.parse_qs(url_components.query)
        print query_dict
        if query_dict.has_key('code'):
            token_info = get_token_from_dropbox(query_dict['code'][0])
        else:
            token_info = "no code param found!"

        print token_info

        # response = echostring + (token_info if token_info else "[token get failed]")

        # self.send_response(200)
        # self.send_header("Content-type", "text/plain")
        # self.send_header("Content-Length", str(len(response)))
        # self.end_headers()
        # self.wfile.write(response)



if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', 4433), StatusServerHandler)
    httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                   keyfile='/home/xgf/bigxgf.key',
                                   certfile='/home/xgf/bigxgf.crt',
                                   server_side=True)
    httpd.serve_forever()

