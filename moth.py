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
                     ret_val=None):
        token = ''.join(
            choice(ascii_letters + digits) for x in range(token_size)
        )

        payload = {'token': token}
        if ip: payload.update(ip=ip)
        if expire:
            expire = (datetime.now() + timedelta(days=expire)).strftime('%s')
            payload.update(expire=expire)
        if ret_val:
            payload.update(ret_val=ret_val)

        self.db.tokens.update({'email': email.lower()},
                              {'$push': {'tokens': payload}},
                              upsert=True)

        return token

    def auth_token(self, token, email, ip=None):
        data = self.db.tokens.find_one({'email': email.lower()})
        logging.info(data)
        if not data: return False

        stored_token = None
        for token_obj in data['tokens']:
            if token_obj['token'] == token:
                stored_token = token_obj
                logging.info('FOUND IT')
                break
        if stored_token is None: return False

        #over-complicated so if the stored token doesn't have an ip,
        #passing one to auth won't return False
        token_ip = stored_token.get('ip')
        if token_ip and ip != token_ip:
            return False

        token_expire = stored_token.get('expire')
        if token_expire and token_expire < datetime.now().strftime('%s'):
            self.remove_token(token, email)
            return False

        ret_val = stored_token.get('ret_val')
        if ret_val: return ret_val
        return True

    def _fetch_user_data(self, email):
        return self.db.tokens.find_one({'email': email.lower()})

    def remove_user(self, email):
        return self.db.tokens.remove({'email': email.lower()})

    def remove_token(self, token, email):
        return self.db.tokens.update({'email': email.lower()},
                                     {'$pull': {'tokens':{'token': token}}})
