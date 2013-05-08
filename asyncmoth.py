#!/usr/bin/env python
from datetime import timedelta, datetime
import logging
from random import choice
from string import ascii_letters, digits

import motor
from tornado.gen import coroutine, Return

class mothError(Exception): pass

class AsyncMoth(object):
    def __init__(self, database='moth', host='localhost', port=27017,
                 user=None, pwd=None):
        if user and pwd:
            connection_string = 'mongodb://%s:%s@%s:%s' % \
                                (user, pwd, host, port)
            self.db = motor.MotorClient(connection_string).open_sync()[database]
        else:
            self.db = motor.MotorClient(host, port).open_sync()[database]

    @coroutine
    def create_token(self, email, ip=None, expire=None, token_size=64,
                     retval=None):
        token = ''.join(
            choice(ascii_letters + digits) for x in range(token_size)
        )
        print token

        payload = {'email': email.lower(), 'token': token}
        if ip:
            payload.update(ip=ip)
        if expire:
            expire = (datetime.now() + timedelta(days=expire)).strftime('%s')
            payload.update(expire=expire)

        yield motor.Op(self.db.tokens.insert, payload)

        if retval:
            yield self.set_retval(email, retval)

        raise Return(token)

    @coroutine
    def auth_token(self, email, token, ip=None):
        criteria = {'email': email.lower(), 'token': token}
        if ip:
            criteria.update(ip=ip)

        data = yield motor.Op(self.db.tokens.find_one, criteria)
        if not data:
            return

        token_ip = data.get('ip', None)
        if token_ip is not None and token_ip != ip:
            return

        token_expire = data.get('expire', None)
        if token_expire is not None and \
        token_expire < datetime.now().strftime('%s'):
            yield self.remove_token(token, email)
            return

        retval = yield self.fetch_retval(email)
        raise Return(retval)

    @coroutine
    def remove_user(self, email):
        yield motor.Op(self.db.tokens.remove, {'email': email.lower()})
        yield motor.Op(self.db.retvals.remove, {'email': email.lower()})

    @coroutine
    def remove_token(self, email, token):
        yield motor.Op(self.db.tokens.remove,
                       {'email': email.lower(), 'token': token})

    @coroutine
    def set_retval(self, email, retval):
        yield motor.Op(self.db.retvals.update, {'email': email.lower()},
                       {'email': email.lower(), 'retval': retval}, upsert=True)
        return

    @coroutine
    def fetch_retval(self, email):
        retval = yield motor.Op(self.db.retvals.find_one,
                                {'email': email.lower()})
        if retval is None: return
        raise Return(retval['retval'])
