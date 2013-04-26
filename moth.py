#!/usr/bin/env python
from datetime import timedelta, datetime
import logging
from random import choice
from string import ascii_letters, digits

from pymongo import MongoClient

class mothError(Exception): pass

class Moth(object):
    def __init__(self, database='moth', host='localhost', port=27017,
                 user=None, pwd=None):
        if user and pwd:
            connection_string = 'mongodb://%s:%s@%s:%s' % \
                                (user, pwd, host, port)
            self.db = MongoClient(connection_string)[database]
        else:
            self.db = MongoClient(host, port)[database]

    def create_token(self, email, ip=None, expire=None, token_size=64,
                     retval=None):
        token = ''.join(
            choice(ascii_letters + digits) for x in range(token_size)
        )

        payload = {'email': email.lower(), 'token': token}
        if ip: payload.update(ip=ip)
        if expire:
            expire = (datetime.now() + timedelta(days=expire)).strftime('%s')
            payload.update(expire=expire)

        self.db.tokens.insert(payload)

        if retval:
            self.set_retval(email, retval)

        return token

    def auth_token(self, email, token, ip=None):
        criteria = {'email': email.lower(), 'token': token}
        if ip: criteria.update(ip=ip)

        data = self.db.tokens.find_one(criteria)
        if not data: return False

        token_expire = data.get('expire')
        if token_expire and token_expire < datetime.now().strftime('%s'):
            self.remove_token(token, email)
            return False

        return self.fetch_retval(email)

    def remove_user(self, email):
        self.db.tokens.remove({'email': email.lower()})
        self.db.retvals.remove({'email': email.lower()})

    def remove_token(self, email, token):
        return self.db.tokens.remove({'email': email.lower(), 'token': token})

    def set_retval(self, email, retval):
        return self.db.retvals.update({'email': email.lower()},
                                      {'email': email.lower(),
                                       'retval': retval},
                                      upsert=True)

    def fetch_retval(self, email):
        retval = self.db.retvals.find_one({'email': email.lower()})
        if retval is None: return None
        return retval.get('retval', None)
