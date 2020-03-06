import os
from os import path
import sys
from requests_oauthlib import OAuth1Session
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
from http import server
from urllib.parse import urlparse
from urllib.parse import parse_qs
from threading import Thread


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class CallbackServer(BaseHTTPRequestHandler):
    @staticmethod
    def wait_path():
        result = { 'path': None }
        httpd = HTTPServer(
            ('0.0.0.0', int(os.environ.get('PORT', '8080'))),
            lambda *args: CallbackServer(lambda path: result.update(path=path), *args)
        )
        httpd.serve_forever()

        return result['path']

    def __init__(self, callback, *args):
        self.callback = callback
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        url = urlparse(self.path)

        if url.path != '/':
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', '0')
            self.end_headers()
        else:
            body = 'ok'.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
            self.connection.close()
            self.callback(self.path)
            th = Thread(target=lambda: self.server.shutdown())
            th.start()

    def log_message(self, format, *args):
        return


def main():
    client_key = os.environ.get('TWITTER_CONSUMER_KEY')
    client_secret = os.environ.get('TWITTER_CONSUMER_SECRET')

    oauth = OAuth1Session(client_key, client_secret=client_secret)

    fetch_response = oauth.fetch_request_token('https://api.twitter.com/oauth/request_token')
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    eprint('Request Token: {}'.format(fetch_response))

    authorization_url = oauth.authorization_url('https://api.twitter.com/oauth/authorize')
    eprint('Authorization URL: {}'.format(authorization_url))

    webbrowser.open_new(authorization_url)

    oauth_response = oauth.parse_authorization_response(CallbackServer.wait_path())
    verifier = oauth_response.get('oauth_verifier')
    eprint('Verifier: {}'.format(verifier))

    oauth = OAuth1Session(
        client_key,
        client_secret=client_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )

    oauth_tokens = oauth.fetch_access_token('https://api.twitter.com/oauth/access_token')
    eprint('OAuth Tokens: {}'.format(oauth_tokens))

    resource_owner_key = oauth_tokens.get('oauth_token')
    resource_owner_secret = oauth_tokens.get('oauth_token_secret')

    oauth = OAuth1Session(
        client_key,
        client_secret=client_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret
    )

    response = oauth.get('https://api.twitter.com/1.1/account/settings.json')
    eprint('Account Settings: {}'.format(response.text))

    print(json.dumps(oauth_tokens))


if __name__ == '__main__':
    main()
