#!/usr/bin/env python

import collections
import hashlib
import json
import requests
import time

__version__ = '1.4.2'


class Phabricator:
    def __init__(self, host, user, cert=None, token=None):
        """
        :param host: Hostname of the Phabricator instance, with no trailing /
        :param user: Your username
        :param cert: The conduit certificate, available in your settings
        """
        self.host = host
        self.user = user
        self.cert = cert
        self.phab_session = {}
        self.token = token
        self.req_session = requests.Session()

    @property
    def connect_params(self):
        token = str(int(time.time()))
        return {
            'client': 'python-fab',
            'clientVersion': __version__,
            'clientDescription': 'A fabulous, lightweight wrapper around Phabricator\'s API',
            'user': self.user,
            'host': self.host,
            'authToken': token,
            'authSignature': hashlib.sha1((str(token) + self.cert).encode()).hexdigest(),
        }

    def connect(self):
        """
        Sets up your Phabricator session, it's not necessary to call
        this directly
        """
        if self.token:
            self.phab_session = {'token': self.token}
            return

        req = self.req_session.post('%s/api/conduit.connect' % self.host, data={
            'params': json.dumps(self.connect_params),
            'output': 'json',
            '__conduit__': True,
        })

        # Parse out the response (error handling ommitted)
        result = req.json()['result']
        self.phab_session = {
            'sessionKey': result['sessionKey'],
            'connectionID': result['connectionID'],
        }

    def request(self, method, params=None):
        """
        Make a request to a method in the phabricator API
        :param method: Name of the API method to call
        :type method: basestring
        :param params: Optional dict of params to pass
        :type params: dict
        """
        if params is None:
            params = {}
        if not self.phab_session:
            self.connect()
        url = '%s/api/%s' % (self.host, method)
        params['__conduit__'] = self.phab_session
        req = self.req_session.post(url, data={
            'params': json.dumps(params),
            'output': 'json',
        })
        return json.loads(
            req.content.decode(),
            object_pairs_hook=collections.OrderedDict
        )['result']
