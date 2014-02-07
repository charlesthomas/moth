#!/usr/bin/env python
# THIS CODE HAS NOT BEEN TESTED AND MAY NOT WORK.
# EVEN IF IT DOES, YOU SHOULDN'T RUN IT.
# IT IS INTENDED TO BE A GUIDE, NOT AN IMPLEMENTATION.

from base64 import b64decode, b64encode
from smtplib import SMTP

from tornado.web import RequestHandler

from moth import Moth


class LoginHandler(RequestHandler):
    moth = Moth()

    def get(self):
        x = self.get_argument('x', '')
        if x == '':
            self.write('''<html><body><form method=POST>Enter your email: <input
                       type=email><input type=submit></form></body></html>''')
        else:
            email, token = b64decode(x).split('&')
            email = email.split('=')[1]
            token = token.split('=')[1]

            if self.moth.auth_token(email=email, token=token) == True:
                self.set_cookie('email', email)
                self.redirect('/dashboard')
            else:
                self.redirect('/login')

    def post(self):
        email = self.get_argument('email')
        fromaddr = "noreply@moth.com"

        token = self.moth.create_token(email=email, expire=1)
        auth_string = b64encode("user=%s&token=%s" % (email, token))

        login_url = "https://login.moth.com/auth?x=%s" % auth_string

        message = "From: %s\r\nTo: %s\r\n\r\nclick to log in:\n%s" % \
            (fromaddr, email, user['fname'], login_url)

        mail_server = SMTP('localhost')
        mail_server.sendmail(fromaddr, email, message)

        self.write('You should be receiving a login link shortly')
