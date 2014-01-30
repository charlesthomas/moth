#!/usr/bin/env python
from unittest import main, TestCase

from pymongo import Connection, MongoClient
from pymongo.errors import ConnectionFailure

from moth import Moth

class MothTestError(Exception): pass

class MothTest(TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.moth = Moth(database='moth_tests')
            cls.mongo = MongoClient()['moth_tests']
        except ConnectionFailure:
            raise MothTestError('Tests need mongo running locally to work')

    @classmethod
    def tearDownClass(cls):
        Connection().drop_database('moth_tests')

    def test_create_token(self):
        email = 'test@token.com'
        token = self.moth.create_token(email)
        self.assertEqual(len(token), 64)

        found = self.mongo.tokens.find_one(dict(email=email, token=token))
        self.assertIsNotNone(found)

        ### WTF IS THIS SHIT? WERE THESE SUPPOSED TO BE AUTH TESTS? ###
        # bad_email = self.mongo.tokens.find_one(dict(email='bad@email.com',
                                               # token=token))
        # self.assertIsNone(bad_email)
# 
        # short_token = self.mongo.tokens.find_one(dict(email=email,
                                                      # token=token[:30]))
        # self.assertIsNone(short_token)
# 
        # long_token = self.mongo.tokens.find_one(dict(email=email,
                                                     # token=token + 'x'))
        # self.assertIsNone(long_token)

    def test_different_sized_tokens(self):
        small_email = 'small@token.com'
        small_token = self.moth.create_token(small_email, token_size=32)
        self.assertEqual(len(small_token), 32)

        found_small = self.mongo.tokens.find_one(dict(email=small_email,
                                                      token=small_token))
        self.assertIsNotNone(found_small)

        large_email = 'large@token.com'
        large_token = self.moth.create_token(large_email, token_size=128)
        self.assertEqual(len(large_token), 128)

        found_large = self.mongo.tokens.find_one(dict(email=large_email,
                                                      token=large_token))
        self.assertIsNotNone(found_large)

    def test_remove_token(self):
        email = 'remove@me.com'
        token = self.moth.create_token(email)
        found = self.mongo.tokens.find_one(dict(email=email, token=token))
        self.assertIsNotNone(found)

        self.moth.remove_token(email=email, token=token)
        not_found = self.mongo.tokens.find_one(dict(email=email, token=token))
        self.assertIsNone(not_found)

    def test_remove_single_token(self):
        email = 'remove_me_too@tokens.com'
        token1 = self.moth.create_token(email)
        token2 = self.moth.create_token(email)

        found1 = self.mongo.tokens.find_one(dict(email=email, token=token1))
        found2 = self.mongo.tokens.find_one(dict(email=email, token=token2))
        self.assertIsNotNone(found1)
        self.assertIsNotNone(found2)

        self.moth.remove_token(email=email, token=token1)
        not_found1 = self.mongo.tokens.find_one(dict(email=email, token=token1))
        still_found2 = self.mongo.tokens.find_one(dict(email=email, token=token2))
        self.assertIsNone(not_found1)
        self.assertIsNotNone(still_found2)

    def test_retval(self):
        email = 'retval@tokens.com'
        want_retval = 'hope this gets returned'
        token = self.moth.create_token(email=email, retval=want_retval)

        got_retval = self.moth.auth_token(email=email, token=token)
        self.assertEqual(want_retval, got_retval)

    def test_remove_user(self):
        email = 'remove_all_the_things@test.com'
        retval = 'this should get wiped'
        token = self.moth.create_token(email=email, retval=retval)
        found_token = self.mongo.tokens.find_one(dict(email=email, token=token))
        self.assertIsNotNone(found_token)

        found_retval = self.mongo.retvals.find_one(dict(email=email,
                                                        retval=retval))
        self.assertIsNotNone(found_retval)

        self.moth.remove_user(email=email)
        not_found_token = self.mongo.tokens.find_one(dict(email=email,
                                                          token=token))
        self.assertIsNone(not_found_token)

        not_found_retval = self.mongo.retvals.find_one(dict(email=email,
                                                            retval=retval))
        self.assertIsNone(not_found_retval)

    def test_auth_vanilla(self):
        email = 'vanilla@user.com'
        token = self.moth.create_token(email)
        authed = self.moth.auth_token(email=email, token=token)
        self.assertTrue(authed)

    def test_non_existant_user(self):
        authed = self.moth.auth_token(email='idont@exist.com',
                                      token='somegarbage')
        self.assertFalse(authed)

    def test_ip_auth(self):
        email = 'ip@freely.com'
        good_ip = '1.2.3.4'
        bad_ip = '10.13.37.42'
        token = self.moth.create_token(email=email, ip=good_ip)

        authed = self.moth.auth_token(email=email, token=token)
        self.assertFalse(authed)

        authed = self.moth.auth_token(email=email, token=token, ip=bad_ip)
        self.assertFalse(authed)

        authed = self.moth.auth_token(email=email, token=token, ip=good_ip)
        self.assertTrue(authed)

    def test_expiration(self):
        email = 'old@man.com'
        token = self.moth.create_token(email=email, expire=-1)
        authed = self.moth.auth_token(email=email, token=token)
        self.assertFalse(authed)

        token = self.moth.create_token(email=email, expire=1)
        authed = self.moth.auth_token(email=email, token=token)
        self.assertTrue(authed)

    def test_the_whole_megillah(self):
        email = 'magilla@gorilla.com'
        ip = '19.64.2.67'
        expire = 2
        retval = 'Allan Melvin'
        token = self.moth.create_token(email=email, ip=ip, expire=expire,
                                       retval=retval)
        authed = self.moth.auth_token(email=email, token=token, ip=ip)
        self.assertEqual(authed, retval)
