fab
===

A fabulous, lightweight wrapper around Phabricator's API, Conduit, to handle
authentication and other annoying things.

Usage
-----

.. code:: python

    import phabricator

    phab = phabricator.Phabricator('https://...', 'Username', token='api-token')
    phab.request('user.whoami')

License
-------
Copyright 2014, 2018 Kunal Mehta, under the GPL v3 or later. See COPYING for more
details.
