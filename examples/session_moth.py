#!/usr/bin/env python
# THIS CODE HAS NOT BEEN TESTED AND MAY NOT WORK.
# EVEN IF IT DOES, YOU SHOULDN'T RUN IT.
# IT IS INTENDED TO BE A GUIDE, NOT AN IMPLEMENTATION.

from tornado.web import RequestHandler

from moth import Moth

class BaseHandler(RequestHandler):
    def get_current_user(self):
        email = self.get_cookie('email', '')
        session_token = self.get_cookie('session', '')
        if email == '' or session == '':
            return False

        return Moth().auth_token(email=email, token=session_token)
