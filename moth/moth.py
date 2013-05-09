#!/usr/bin/env python
from datetime import timedelta, datetime
import logging
from random import choice
from string import ascii_letters, digits

from pymongo import MongoClient

class mothError(Exception): pass

class Moth(object):
    '''
    Moth is an email-only authentication scheme
    e-mail auth -> mauth -> moth

    Sending mail is easy enough with smtplib. Moth doesn't actually send the
    mail, but it generates tokens, and validates them based on email address,
    and (optionally) ip address and expiration.
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
            self.db = MongoClient(connection_string)[database]
        else:
            self.db = MongoClient(host, port)[database]

    def create_token(self, email, ip=None, expire=None, token_size=64,
                     retval=None):
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
        if ip: payload.update(ip=ip)
        if expire:
            expire = (datetime.now() + timedelta(days=expire)).strftime('%s')
            payload.update(expire=expire)

        self.db.tokens.insert(payload)

        if retval:
            self.set_retval(email, retval)

        return token

    def auth_token(self, email, token, ip=None):
        '''
        return true if email address and token match. if ip exists, also verify
        that. if expiration was set when create_token was called, verify that
        the token hasn't expired.
        if for any reason the token is not valid, remove it
        '''
        criteria = {'email': email.lower(), 'token': token}
        if ip: criteria.update(ip=ip)

        data = self.db.tokens.find_one(criteria)
        if not data: return False

        token_ip = data.get('ip', None)
        if token_ip is not None and token_ip != ip:
            self.remove_token(token, email)
            return False

        token_expire = data.get('expire', None)
        if token_expire and token_expire < datetime.now().strftime('%s'):
            self.remove_token(token, email)
            return False

        return self.fetch_retval(email)

    def remove_user(self, email):
        '''
        remove all user data from Moth
        '''
        self.db.tokens.remove({'email': email.lower()})
        self.db.retvals.remove({'email': email.lower()})

    def remove_token(self, email, token):
        '''
        remove token from Moth
        '''
        return self.db.tokens.remove({'email': email.lower(), 'token': token})

    def set_retval(self, email, retval):
        '''
        store retval associated with the email address
        when auth_token is called, if the authentication was successful, and a
        retval exists, it will be returned by the auth_token call. if retval
        does not exist, auth_token returns True
        '''
        return self.db.retvals.update({'email': email.lower()},
                                      {'email': email.lower(),
                                       'retval': retval},
                                      upsert=True)

    def fetch_retval(self, email):
        '''
        if retval exists, return it
        if it doesn't, return True
        '''
        retval = self.db.retvals.find_one({'email': email.lower()})
        if retval is None:
            return True
        return retval.get('retval', True)
