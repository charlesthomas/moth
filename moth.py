#!/usr/bin/env python
from string import ascii_letters, digits
from random import choice
from datetime import timedelta, datetime

class mothException(Exception): pass

class Moth(object):
    def __init__(self, collection):
        self.collection = collection

    def create_token(self, email, ip=None, expire=None, token_size=64,
                     ret_val=None):
        token = ''.join(
            choice(ascii_letters + digits) for x in range(token_size)
        )

        if self.store_token(token, email, ip, expire, ret_val):
            return token

        raise mothException("failed to store token")

    def auth_token(self, token, email, ip=None):
        user = self.fetch_user_data(email)
        if not user: return False

        if token not in user['token']: return False

        #over-complicated so if the stored token doesn't have an ip,
        #passing one to auth won't return False
        token_ip = user['token'][token].get('ip')
        if token_ip and ip != token_ip:
            return False

        token_expire = user['token'][token].get('expire')
        if token_expire and token_expire < datetime.now().strftime('%s'):
            self.remove_token(token, email)
            return False

        ret_val = user['token'][token].get('ret_val')
        if ret_val: return ret_val
        return True

    def store_token(self, token, email, ip=None, expire=None, ret_val=None):
        payload = {}
        if ip: payload['ip'] = ip
        if ret_val: payload['ret_val'] = ret_val
        if expire:
            expire = datetime.now() + timedelta(days = expire)
            payload['expire'] = expire.strftime('%s')
        
        existing = self.fetch_user_data(email)
        if existing:
            tokens = existing['token']
            tokens[token] = payload

            return self.collection.update(
                { '_id' : existing['_id'] },
                { "$set" : { 'token' : tokens } }
            )

        return self.collection.insert({
            'token' : { token : payload },
            'email' : email.lower(),
        })

    def fetch_user_data(self, email):
        return self.collection.find_one({ 'email' : email.lower() })

    def remove_user(self, id):
        return self.collection.remove(id)

    def remove_token(self, token, email):
        user = self.fetch_user_data(email)
        if not token in user['token']:
            raise mothException("token doesn't exist")

        tokens = user['token']
        tokens.pop(token)
        return self.collection.update(
            { '_id' : user['_id'] },
            { "$set" : { 'token' : tokens } }
        )
