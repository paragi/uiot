# uweb - micropython extreme minimal webserver
# (c) Simon Rigét @ paragi 2022
# Released under MIT licence

# captive portal:
# https://github.com/anson-vandoren/esp8266-captive-portal
# https://lemariva.com/blog/2019/01/white-hacking-wemos-captive-portal-using-micropython
PC = 1
ESP = 2
try:
    import network
    import usocket as socket
    import uasyncio as asyncio

    platform = ESP
except:
    import socket
    import asyncio

    platform = PC
import gc
import os

try:
    from common import *
except:
    debug = print

# TODO: redirect https -> http af hensyn til store browsere
MAX_LEN_RECIEVE = 1024
READ_TIMEOUT_MS = 1000
SEND_BUFFER_SIZE = 128
MIMETYPE = {
    'html': 'text/html; charset=utf-8',
    'css': 'text/css',
    'ico': 'image/x-icon',
    'png': 'image/png',
    'gif': 'image/gif',
    'jpg': 'image/jpg',
    'json': 'application/json'
}
STATIC_FILE_HEADER = header = \
    'HTTP/1.x 200 OK\r\n' \
    'Content-Type: {0}\r\n' \
    'Cache-Control: public, max - age = 15552000\r\n' \
    '\r\n'
HEADER_NOT_FOUND = 'HTTP/1.x 404 Not Found\r\n\r\n'


class Request:
    def __init__(self):
        self._header_lines = []
        self._method = ''
        self._uri = ''
        self._body_raw = ''
        self.protocol = ''
        self._path = ''
        self._header = {}
        self._body = {}

    def method(self):
        if not self._method:
            try:
                (self._method, self._uri, self.protocol) = self._header_lines[0].split(' ', 2)
            except ValueError:
                pass

        return self._method

    def path(self):
        if not self._path:
            if not self._uri:
                self.method()
            (self._path, sep, self._query) = self._uri.partition('?')
        return self._path

    def query(self):
        if not self._query:
            if not self._query:
                self.path()
            self._querys = self._query.split('&')
        return self._path

    def headers(self):
        if not len(self._header):
            for line in self._header_lines:
                try:
                    (key, value) = line.split(': ')
                    self._header[key] = value
                except:
                    pass
        return self._header

    def body(self):
        if not len(self._body):
            if len(self._body_raw):
                encoding = None
                if 'Content-Type' in self.headers().keys():
                    encoding = self.headers()['Content-Type']
                if not encoding or encoding == 'application/x-www-form-urlencoded':
                    for line in self._body_raw.split('\r\n'):
                        (key, value) = line.split('=', 1)
                        self._body[key] = value
                elif encoding == 'application/json':
                    import json
                    self._body = json.loads(self._body_raw)
        return self._body


class Webserver():
    def __init__(self, host='0.0.0.0', port=80, dyn_handler=None, docroot=''):
        self.host = host
        self.port = port
        self.docroot = docroot
        if dyn_handler:
            self.dyn_handler = dyn_handler
        else:
            self.dyn_handler = self.hello_dyn_handler

    async def hello_dyn_handler(self, request, writer):
        await writer.awrite('HTTP/1.x 200 OK\r\n' \
               'Content-Type: text/html; charset=UTF-8\r\n' \
               '\r\n' \
               '<!DOCTYPE html><html>\n' \
               '<body><h1>Welcome to CP-IOT webserver</h1></body>' \
               '</html>'
        .encode('utf8'))

    async def handle_client(self, reader, writer):
        while True:  # Run once
            request = Request()
            # Read headers
            while True:
                try:
                    line = await asyncio.wait_for(reader.readline(), READ_TIMEOUT_MS)
                except asyncio.TimeoutError:
                    debug("Read timeout while reading headers from client request")
                    break
                if line == b'\r\n': break
                request._header_lines.append(line.decode('utf8').rstrip())
            debug(f"Recieved client request: {request._header_lines[0]}")

            # Serve static file
            ext = request.path().rpartition('.')[2]
            if ext in MIMETYPE.keys():
                debug(f"Request file: {request.path()}")
                if request.path()[1:] in os.listdir(self.docroot):
                    writer.write(STATIC_FILE_HEADER.format(MIMETYPE[ext]).encode('utf-8'))
                    await writer.drain()
                    with open(self.docroot + request.path(), 'rb') as file_handle:
                        while chunck := file_handle.read(SEND_BUFFER_SIZE):
                            writer.write(chunck)
                else:
                    writer.write(HEADER_NOT_FOUND.encode('utf-8'))

            # Serve dynamic content
            else:
                body_length = 0
                for header in request._header_lines:
                    if not header.startswith("Content-Length:"): continue
                    body_length = min(int(header.split(': ')[1]), MAX_LEN_RECIEVE)
                    break

                if body_length > 0:
                    debug(f"Reading body length={body_length} bytes:", DEBUG)
                    try:
                        request._body_raw = (await asyncio.wait_for(reader.read(body_length), READ_TIMEOUT_MS)).decode(
                            'utf8')
                        debug(request._body_raw, DEBUG)
                    except asyncio.TimeoutError:
                        debug("Read timeout while reading body")
                        break

                debug("Sending response")
                if self.dyn_handler:
                    await self.dyn_handler(request, writer)

            await writer.drain()
            break
        writer.close()
        # if platform != PC: await writer.closed()
        gc.collect()

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        return self.server
