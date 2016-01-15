#!/usr/bin/python

import SimpleHTTPServer
import BaseHTTPServer
import socket
import ssl
import httplib
import urllib
import urlparse
import traceback
import logging

__version__ = "0.1"

response_template = """<html>
<head>
  <title>%s</title>
</head>
<body>
%s
</body>
</html>
"""


class OAuthTokenHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    server_version = "StatusServer" + __version__
    timeout = 0.5
    token_dict = dict()

    def do_GET(self):
        logging.info("get a request: %s", self.path)
        if self.path.find("easyspace") == -1:
            logging.warning("ignore request: %s", self.path)
            return

        url_components = urlparse.urlparse(self.path)

        mimetype = "text/html"
        try:
            if url_components.path == "/easyspace-baidu/gettoken":
                response = self.search_token(url_components)
                mimetype = "text/json"
            else:
                self.download_token_by_code(url_components)
                response = response_template % ("OAuth Succeed", "<H1>please obtain token!</H1>")
        except Exception, e:
            logging.error(e.message)
            response = response_template % ("Failed", traceback.format_exc())

        self.send_response(200)
        self.send_header("Content-Type", mimetype)
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def download_token_by_code(self, url_components):
        query_dict = urlparse.parse_qs(url_components.query)

        if "code" not in query_dict or "state" not in query_dict:
            raise "invalid request: ", self.path

        code = query_dict['code'][0]
        if url_components.path == "/easyspace-dropbox":
            token_info = OAuthTokenHandler.get_token_from_dropbox(code)
        elif url_components.path == "/easyspace-baidu":
            token_info = OAuthTokenHandler.get_token_from_baidu(code)
        else:
            raise "invalid uri:" + url_components.path

        state = query_dict['state'][0]
        if token_info:
            OAuthTokenHandler.token_dict[state] = token_info

        logging.info("token_dict: %s", str(OAuthTokenHandler.token_dict))
        return token_info

    @staticmethod
    def search_token(url_components):
        query_dict = urlparse.parse_qs(url_components.query)
        if "state" in query_dict:
            state = query_dict["state"][0]
            if state in OAuthTokenHandler.token_dict:
                return OAuthTokenHandler.token_dict[state]
            else:
                raise "gettoken failed, token_dict: " + OAuthTokenHandler.token_dict
        else:
            raise "no state param in request url"

    @staticmethod
    def get_token_from_baidu(code):
        params = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": "QoPCF5Pi8xRB6IeQQp5R1BHb",
            "client_secret": "jeFAGpNYqQMQllYI7qLeOOssmrM5QNqq",
            "redirect_uri": "https://172.23.2.180:4433/easyspace-baidu"
        }
        posturl = "/oauth/2.0/token?" + urllib.urlencode(params)

        post_client = httplib.HTTPSConnection(host="openapi.baidu.com", port=443, timeout=30)
        try:
            post_client.request(method="POST", url=posturl)
            resp = post_client.getresponse().read()
        except socket.timeout, e:
            logging.error("get_token_from_baidu failed, reason:", e.message)
            resp = None
        return resp

    @staticmethod
    def get_token_from_dropbox(code):
        params = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': 'q4nbe7oeonl0dhu',
            'client_secret': 'vf6lbqlthlul1il',
            'redirect_uri': 'https://big.xgf.ren:4433/easyspace-dropbox'
        }
        posturl = "/1/oauth2/token?" + urllib.urlencode(params)

        client = httplib.HTTPSConnection(host='api.dropboxapi.com', port=443, timeout=30)
        try:
            client.request(method="POST", url=posturl)
            resp = client.getresponse().read()
        except socket.timeout, e:
            logging.error("get_token_from_dropbox failed: %s", e.message)

        return resp


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)-8s %(message)s - %(filename)s:%(lineno)d',
                        level=logging.DEBUG)
    httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', 4433), OAuthTokenHandler)
    httpd.socket = ssl.wrap_socket(sock=httpd.socket,
                                   keyfile='/home/xue_guangfeng/bigxgf.key',
                                   certfile='/home/xue_guangfeng/bigxgf.crt',
                                   server_side=True)
    httpd.serve_forever()

