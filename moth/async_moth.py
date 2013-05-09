#!/usr/bin/env python
from datetime import timedelta, datetime
from random import choice
from string import ascii_letters, digits

from motor import MotorClient, Op
from tornado.gen import engine, Task

class mothError(Exception): pass

class AsyncMoth(object):
    '''
    Moth is an email-only authentication scheme
    e-mail auth -> mauth -> moth

    Sending mail is easy enough with smtplib. Moth doesn't actually send the
    mail, but it generates tokens, and validates them based on email address,
    and (optionally) ip address and expiration.

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

    @engine
    def create_token(self, email, ip=None, expire=None, token_size=64,
                     retval=None, callback=None):
        '''
        generate a token of a given length, tied to email address, and store it
        optionally store ip address, expiration (in days), and retval (see
        set_retval for additional information on this)
        return the token
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

        callback(token)

    @engine
    def auth_token(self, email, token, ip=None, callback=None):
        '''
        return true if email address and token match. if ip exists, also verify
        that. if expiration was set when create_token was called, verify that
        the token hasn't expired.
        if for any reason the token is not valid, remove it
        '''
        criteria = {'email': email.lower(), 'token': token}
        if ip:
            criteria.update(ip=ip)

        data = yield Op(self.db.tokens.find_one, criteria)
        if not data:
            callback(False)

        token_ip = data.get('ip', None)
        if token_ip is not None and token_ip != ip:
            callback(False)

        token_expire = data.get('expire', None)
        if token_expire is not None and \
        token_expire < datetime.now().strftime('%s'):
            yield Task(self.remove_token, token, email)
            callback(False)

        retval = yield Task(self.fetch_retval, email)
        if retval is None:
            callback(True)
        else:
            callback(retval)

    @engine
    def remove_user(self, email, callback):
        '''
        remove all user data from Moth
        '''
        yield Op(self.db.tokens.remove, {'email': email.lower()})
        yield Op(self.db.retvals.remove, {'email': email.lower()})
        callback()

    @engine
    def remove_token(self, email, token, callback):
        '''
        remove token from Moth
        '''
        yield Op(self.db.tokens.remove,
                       {'email': email.lower(), 'token': token})
        callback()

    @engine
    def set_retval(self, email, retval, callback):
        '''
        store retval associated with the email address
        when auth_token is called, if the authentication was successful, and a
        retval exists, it will be returned by the auth_token call. if retval
        does not exist, auth_token returns True
        '''
        yield Op(self.db.retvals.update, {'email': email.lower()},
                       {'email': email.lower(), 'retval': retval}, upsert=True)
        callback()

    @engine
    def fetch_retval(self, email, callback):
        '''
        if retval exists, return it
        if it doesn't, return True
        '''
        result = yield Op(self.db.retvals.find_one,
                                {'email': email.lower()})
        if result is None:
            callback(None)
        else:
            callback(result.get('retval', True))
