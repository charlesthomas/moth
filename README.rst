====
moth
====
.. image:: https://travis-ci.org/charlesthomas/moth.png?branch=master
        :target: https://travis-ci.org/charlesthomas/moth

**Moth** was conceived to be used as an email-only authentication scheme (mail
auth -> mauth -> moth), however, it is generic enough to be used for pretty much
any token-based authentication.

Relevant Links
--------------
- `moth in PyPI`_
- `moth on Github`_
- `moth documentation`_
- `moth build status`_
- `moth author`_

Synchronous vs. Asynchronous
----------------------------
To create a synchronous moth object: ::

    from moth import Moth
    moth_object = Moth()

To create an asynchronous moth object: ::

    from moth import AsyncMoth
    moth_object = AsyncMoth()

All method calls are supported and identically named in **Moth** vs.
**AsyncMoth**. For the rest of this README, **Moth** will refer to both **Moth**
and **AsyncMoth** unless stated otherwise.

Initialization
--------------
Initiating **Moth** takes the credentials for creating a connection to MongoDB,
as well as the database name (which defaults to "moth").

``AsyncMoth.__init__()`` **blocks while creating a connection.** It is the only
method which does so. It is recommended that you initialize **AsyncMoth** as
part of your tornado server's startup.

Creating Tokens
---------------
Calling ``moth.create_token()`` generates a random token and stores it along
with email address and optional IP address, expiration (in days), and retval.
The method returns the token.

Authenticating Tokens
---------------------
Calling ``moth.auth_token()`` queries mongo for the passed email/token
combination. If IP address is in the record returned from mongo, it is
validated. If expiration is returned, it is compared to ``datetime.now()``

**If either IP address or expiration fails to validate, the token will be
deleted.**

If the token validates, retval is queried. If a retval exists, it is returned.
If it doesn't, ``moth.auth_token()`` returns True.

Additional Methods
------------------
All other methods are fairly self explanatory, and/or mostly for internal
purposes. Read the code to figure out how it works.

What is retval?
---------------
retval is the value that will be returned when ``moth.auth_token()`` is
successful. It is **completely optional**. If you don't pass a retval to
``moth.create_token()``, and don't call ``moth.set_retval()``, then
``moth.auth_token()`` will return True on successful calls.

Why use it?
~~~~~~~~~~~
For the project I'm working on which lead to the creation of **Moth**, retval is
an OAuth token. When I call ``moth.auth_token()``, I validate the moth token,
which gives me the user's OAuth token for making API calls.

Requirements
------------
**Moth** requires **Motor**, as well as **Tornado** and **Pymongo** (which are
both installed via **Motor**).

Examples
--------
Examples can be found on `ReadTheDocs`_

.. _moth in PyPI: https://pypi.python.org/pypi/moth
.. _moth on Github: https://github.com/charlesthomas/moth
.. _moth documentation: https://moth.readthedocs.org/en/latest/moth.html
.. _moth build status: https://travis-ci.org/charlesthomas/moth
.. _moth author: mailto:ch@rlesthom.as
.. _ReadTheDocs: http://moth.readthedocs.org/en/latest/examples.html
