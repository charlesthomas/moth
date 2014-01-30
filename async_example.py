#!/usr/bin/env python
import logging

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, asynchronous

from moth import AsyncMoth

class TestHandler(RequestHandler):
    @asynchronous
    @gen.engine
    def get(self):
        email = 'ch@rlesthom.as'
        want_retval = 'test retval'
        moth = server.settings['moth']

        ### create_token ###
        self.write('test create_token...<br>')
        token = yield gen.Task(moth.create_token, email, retval=want_retval)
        self.write(token + '<br>')

        ### auth_token ###
        self.write('test auth_token...<br>')
        have_retval = yield gen.Task(moth.auth_token, email, token)
        self.write('"%s" should match "%s"<br>' % (want_retval, have_retval))

        ### auth_token for invalid email ###
        self.write('test bad auth...<br>')
        should_be_False = yield gen.Task(moth.auth_token, 'fake@f.com', token)
        self.write('"%s" should be False<br>' % should_be_False)

        ### remove_token ###
        self.write('test remove_token...<br>')
        yield gen.Task(moth.remove_token, email, token)

        ### set_retval ###
        # if create_token and auth_token work, this works

        ### fetch_retval ###
        # if create_token and auth_token work, this works

        ### remove_user ###
        self.write('test remove_user...<br>')
        yield gen.Task(moth.remove_user, email)

        self.finish()

server = Application([('/', TestHandler)], debug=True)
server.settings['moth'] = AsyncMoth('moth_test')
server.listen(9000)
IOLoop.instance().start()
