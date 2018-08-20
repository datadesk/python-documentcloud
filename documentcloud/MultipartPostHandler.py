#!/usr/bin/python

####
# 02/2006 Will Holcomb <wholcomb@gmail.com>

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# 7/26/07 Slightly modified by Brian Schneider
# in order to support unicode files ( multipart_encode function )
"""
Usage:
  Enables the use of multipart/form-data for posting forms

Inspirations:
  Upload files in python:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
  urllib2_file:
    Fabien Seisen: <fabien@seisen.org>

Example:
  import MultipartPostHandler, urllib2, cookielib

  cookies = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),
                                MultipartPostHandler.MultipartPostHandler)
  params = { "username" : "bob", "password" : "riviera",
             "file" : open("filename", "rb") }
  opener.open("http://wwww.bobsite.com/upload/", params)

Further Example:
  The main function of this file is a sample which downloads a page and
  then uploads it to the W3C validator.
"""
import os
import sys
import six
import tempfile
import mimetypes
from os import SEEK_END
if six.PY3:
    import io
    import urllib.parse
    import urllib.request
    from email.generator import _make_boundary as choose_boundary
else:
    import cStringIO as io
    from six.moves import urllib
    from mimetools import choose_boundary

# Controls how sequences are uncoded. If true, elements
# may be given multiple values byassigning a sequence.
doseq = 1


class PostHandler(urllib.request.BaseHandler):
    handler_order = urllib.request.HTTPHandler.handler_order - 10

    def http_request(self, request):
        try:
            data = request.get_data()
        except AttributeError:
            data = request.data
        if data is not None and type(data) != str:
            data = urllib.parse.urlencode(data, doseq).encode("utf-8")
            try:
                request.add_data(data)
            except AttributeError:
                request.data = data
        return request
    https_request = http_request


class MultipartPostHandler(urllib.request.BaseHandler):
    # needs to run first
    handler_order = urllib.request.HTTPHandler.handler_order - 10

    def http_request(self, request):
        try:
            data = request.get_data()
        except AttributeError:
            data = request.data
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                for(key, value) in list(data.items()):
                    if hasattr(value, 'read'):
                        v_files.append((key, value))
                    else:
                        v_vars.append((key, value))
            except TypeError:
                raise TypeError
            if len(v_files) == 0:
                data = urllib.parse.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if (
                    request.has_header('Content-Type') and
                    request.get_header('Content-Type').find(
                        'multipart/form-data') != 0
                ):
                    six.print_(
                        "Replacing %s with %s" % (
                            request.get_header('content-type'),
                            'multipart/form-data'
                        )
                    )
                request.add_unredirected_header('Content-Type', contenttype)
            try:
                request.add_data(data)
            except AttributeError:
                request.data = data

        return request

    def multipart_encode(self, v_vars, files, boundary=None, buf=None):
        if six.PY3:
            if boundary is None:
                boundary = choose_boundary()
            if buf is None:
                buf = io.BytesIO()
            for(key, value) in v_vars:
                buf.write(b'--' + boundary.encode("utf-8") + b'\r\n')
                buf.write(
                    b'Content-Disposition: form-data; name="' +
                    key.encode("utf-8") +
                    b'"'
                )
                buf.write(b'\r\n\r\n' + value.encode("utf-8") + b'\r\n')
            for(key, fd) in files:
                try:
                    filename = fd.name.split('/')[-1]
                except AttributeError:
                    # Spoof a file name if the object doesn't have one.
                    # This is designed to catch when the user submits
                    # a StringIO object
                    filename = 'temp.pdf'
                contenttype = mimetypes.guess_type(filename)[0] or \
                    b'application/octet-stream'
                buf.write(b'--' + boundary.encode("utf-8") + b'\r\n')
                buf.write(
                    b'Content-Disposition: form-data; ' +
                    b'name="' + key.encode("utf-8") + b'"; ' +
                    b'filename="' + filename.encode("utf-8") + b'"\r\n'
                )
                buf.write(
                    b'Content-Type: ' +
                    contenttype.encode("utf-8") +
                    b'\r\n'
                )
                fd.seek(0)
                buf.write(
                    b'\r\n' + fd.read() + b'\r\n'
                )
            buf.write(b'--')
            buf.write(boundary.encode("utf-8"))
            buf.write(b'--\r\n\r\n')
            buf = buf.getvalue()
            return boundary, buf
        else:
            if boundary is None:
                boundary = choose_boundary()
            if buf is None:
                buf = io.StringIO()
            for(key, value) in v_vars:
                buf.write('--%s\r\n' % boundary)
                buf.write('Content-Disposition: form-data; name="%s"' % key)
                buf.write('\r\n\r\n' + value + '\r\n')
            for(key, fd) in files:
                try:
                    filename = fd.name.split('/')[-1]
                except AttributeError:
                    # Spoof a file name if the object doesn't have one.
                    # This is designed to catch when the user submits
                    # a StringIO object
                    filename = 'temp.pdf'
                contenttype = mimetypes.guess_type(filename)[0] or \
                    'application/octet-stream'
                buf.write('--%s\r\n' % boundary)
                buf.write('Content-Disposition: form-data; \
    name="%s"; filename="%s"\r\n' % (key, filename))
                buf.write('Content-Type: %s\r\n' % contenttype)
                # buffer += 'Content-Length: %s\r\n' % file_size
                fd.seek(0)
                buf.write('\r\n' + fd.read() + '\r\n')
            buf.write('--' + boundary + '--\r\n\r\n')
            buf = buf.getvalue()
            return boundary, buf
    https_request = http_request


def getsize(o_file):
    """
    get the size, either by seeeking to the end.
    """
    startpos = o_file.tell()
    o_file.seek(0)
    o_file.seek(0, SEEK_END)
    size = o_file.tell()
    o_file.seek(startpos)
    return size


def main():
    opener = urllib.request.build_opener(MultipartPostHandler)

    def validateFile(url):
        temp = tempfile.mkstemp(suffix=".html")
        os.write(temp[0], opener.open(url).read())
        os.remove(temp[1])

    if len(sys.argv[1:]) > 0:
        for arg in sys.argv[1:]:
            validateFile(arg)
    else:
        validateFile("http://www.google.com")


if __name__ == "__main__":
    main()
