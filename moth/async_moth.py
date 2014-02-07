#!/usr/bin/env python
from datetime import timedelta, datetime
from random import choice
from string import ascii_letters, digits

from motor import MotorClient, Op
from tornado.gen import coroutine, Return, Task

class AsyncMoth(object):
    '''
    :class:`AsyncMoth` blocks on ``__init__`` when opening the MongoDB
    connection. All params are for creating said connection.

    AsyncMoth is functionally equivalent to Moth, but with asynchronous support
    for use with Tornado/Motor.
    '''
    def __init__(self, database='moth', host='localhost', port=27017,
                 user=None, pwd=None):
        '''
        Moth uses a mongo back-end (although other data stores may be added
        later) __init__ creates a mongo connection with the passed credentials.
        '''
        if user and pwd:
            connection_string = 'mongodb://%s:%s@%s:%s' % \
                                (user, pwd, host, port)
        else:
            connection_string = 'mongodb://%s:%s' % \
                                (host, port)

        self.db = MotorClient(connection_string).open_sync()[database]

    @coroutine
    def create_token(self, email, ip=None, expire=None, token_size=64,
                     retval=None):
        '''
        Generate a token of a given length, tied to email address, and store it.
        Optionally store ip address, expiration (in days), and retval (see
        set_retval for additional information on this).
        Return the token.
        '''
        token = ''.join(
            choice(ascii_letters + digits) for x in range(token_size)
        )

        payload = {'email': email.lower(), 'token': token}
        if ip:
            payload.update(ip=ip)
        if expire:
            expire = (datetime.now() + timedelta(days=expire)).strftime('%s')
            payload.update(expire=expire)

        yield Op(self.db.tokens.insert, payload)

        if retval:
            yield Task(self.set_retval, email, retval)

        raise Return(token)

    @coroutine
    def auth_token(self, email, token, ip=None):
        '''
        Return True if email address and token match. If IP exists, also verify
        that. If expiration was set when create_token was called, verify that
        the token hasn't expired.
        If for any reason the token is not valid, remove it.
        '''
        criteria = {'email': email.lower(), 'token': token}
        if ip:
            criteria.update(ip=ip)

        data = yield Op(self.db.tokens.find_one, criteria)
        if not data:
            raise Return(False)

        token_ip = data.get('ip', None)
        if token_ip is not None and token_ip != ip:
            raise Return(False)

        token_expire = data.get('expire', None)
        if token_expire is not None and \
        token_expire < datetime.now().strftime('%s'):
            yield Task(self.remove_token, token, email)
            raise Return(False)

        retval = yield Task(self.fetch_retval, email)
        if retval is None:
            raise Return(True)
        else:
            raise Return(retval)

    @coroutine
    def remove_user(self, email):
        '''
        Remove all user data from Moth
        '''
        yield Op(self.db.tokens.remove, {'email': email.lower()})
        yield Op(self.db.retvals.remove, {'email': email.lower()})

    @coroutine
    def remove_token(self, email, token):
        '''
        Remove token from Moth
        '''
        yield Op(self.db.tokens.remove,
                       {'email': email.lower(), 'token': token})

    @coroutine
    def set_retval(self, email, retval):
        '''
        Store retval associated with the email address.  When ``auth_token`` is
        called, if the authentication was successful, and a retval exists, it
        will be returned by the auth_token call. If retval does not exist,
        auth_token returns True.
        '''
        yield Op(self.db.retvals.update, {'email': email.lower()},
                       {'email': email.lower(), 'retval': retval}, upsert=True)

    @coroutine
    def fetch_retval(self, email):
        '''
        If retval exists, return it.
        If it doesn't, return True.
        '''
        result = yield Op(self.db.retvals.find_one,
                                {'email': email.lower()})
        if result is None:
            raise Return(None)
        else:
            raise Return(result.get('retval', True))
