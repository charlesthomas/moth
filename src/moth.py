#!/usr/bin/env python
from string import ascii_letters, digits
from random import choice

class mothException( Exception ): pass

class Moth( object ):
    def __init__( self, collection ):
        self.collection = collection

    def create_token( self, address, token_size = 64 ):
        token = ''.join(
            choice( ascii_letters + digits ) for x in range( token_size )
        )

        if self.store_token( token, address ):
            return token

        raise mothException( "failed to store token" )

    def auth_token( self, token, address ):
        user = self.fetch_user_data( address )
        if not user: return False
        if token in user[ 'token' ]: return True
        return False
        
    def store_token( self, token, address ):
        existing = self.fetch_user_data( address )
        if existing:
            tokens = existing[ 'token' ]
            tokens.append( token )
            return self.collection.update(
                { '_id' : existing[ '_id' ] },
                { "$set" : { 'token' : tokens } }
            )

        return self.collection.insert( {
            'token' : [ token ],
            'address' : address.lower(),
        } )

    def fetch_user_data( self, address ):
        return self.collection.find_one( { 'address' : address.lower() } )

    def remove_user( self, id ):
        return self.collection.remove( id )

    def remove_token( self, token, address ):
        user = self.fetch_user_data( address )
        if not token in user[ 'token' ]:
            raise mothException( "token doesn't exist" )

        tokens = user[ 'token' ]
        tokens.pop( tokens.index( token ) )
        return self.collection.update(
            { '_id' : user[ '_id' ] },
            { "$set" : { 'token' : tokens } }
        )
