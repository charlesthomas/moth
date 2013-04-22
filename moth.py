#!/usr/bin/env python
from string import ascii_letters, digits
from random import choice
from datetime import timedelta, datetime

class mothException(Exception): pass

class Moth(object):
    def __init__(self, collection):
        self.collection = collection

    def create_nonce(self, email, expire=300, ip=None, nonce_size=32):
        nonce = ''.join(
            choice(ascii_letters + digits) for x in range(nonce_size)
        )

        if self.store_nonce(nonce, email, expire, ip):
            return nonce

        raise mothException("failed to store nonce")

    def create_token(self, email, nonce, ip=None, expire=None, token_size=64,
                     ret_val=None):
        if not self._auth_nonce(nonce, email, ip):
            raise mothException('failed to authorize nonce')

        token = ''.join(
            choice(ascii_letters + digits) for x in range(token_size)
        )

        if self.store_token(token, email, ip, expire, ret_val):
            return token

        raise mothException("failed to store token")

    def _auth_nonce(self, nonce, email, ip=None):
        user = self._fetch_user_data(email)
        if not user: return False
        if nonce not in user.get('nonce', {}): return False

        self.remove_nonce(nonce, email)

        nonce_ip = user['nonce'][nonce].get('ip')
        if nonce_ip and ip != nonce_ip:
            return False

        nonce_expire = user['nonce'][nonce]['expire']
        if nonce_expire < datetime.now().strftime('%s'):
            return False

        return True

    def auth_token(self, token, ip=None):
        user = self._fetch_user_data(token=token)
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

    def store_nonce(self, nonce, email, expire=300, ip=None):
        payload = {}
        if ip: payload['ip'] = ip
        expire = (datetime.now() + timedelta(seconds=expire)).strftime('%s')
        payload['expire'] = expire

        return self.collection.update(
            {'email': email},
            {'$set':{'nonce': {nonce: payload}}},
            upsert=True
        )

    def store_token(self, token, email, ip=None, expire=None, ret_val=None):
        payload = {}
        if ip: payload['ip'] = ip
        if ret_val: payload['ret_val'] = ret_val
        if expire:
            expire = datetime.now() + timedelta(days = expire)
            payload['expire'] = expire.strftime('%s')
        
        existing = self._fetch_user_data(email=email)
        if existing:
            tokens = existing.get('token', {})
            tokens[token] = payload

            return self.collection.update(
                { '_id' : existing['_id'] },
                { "$set" : { 'token' : tokens } }
            )

        return self.collection.insert({
            'token' : { token : payload },
            'email' : email.lower(),
        })

    def _fetch_user_data(self, email=None, token=None):
        if email:
            return self.collection.find_one({ 'email' : email.lower() })
        if token:
            return self.collection.find_one({'token': {token: {}}})

    def remove_user(self, id):
        return self.collection.remove(id)

    def remove_nonce(self, nonce, email):
        return self.collection.update(
            {'email': email},
            {'$unset': {'nonce': {nonce: {}}}}
        )

    def remove_token(self, token, email):
        user = self._fetch_user_data(email)
        if not token in user['token']:
            raise mothException("token doesn't exist")

        tokens = user['token']
        tokens.pop(token)
        return self.collection.update(
            { '_id' : user['_id'] },
            { "$set" : { 'token' : tokens } }
        )
