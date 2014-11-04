#!/usr/bin/env python

import collections
import hashlib
import json
import requests
import time


class Phabricator:
    def __init__(self, host, user, cert):
        """
        :param host: Hostname of the Phabricator instance, with no trailing /
        :param user: Your username
        :param cert: The conduit certificate, available in your settings
        """
        self.host = host
        self.user = user
        self.cert = cert
        self.phab_session = {}
        self.token = int(time.time())
        self.signature = hashlib.sha1(str(self.token) + self.cert).hexdigest()
        self.req_session = requests.Session()

    @property
    def connect_params(self):
        return {
            'client': 'phab-bz',
            'clientVersion': 0,
            'clientDescription': 'A script for importing Bugzilla bugs into Phabricator',
            'user': self.user,
            'host': self.host,
            'authToken': self.token,
            'authSignature': self.signature,
        }

    def connect(self):
        """
        Sets up your Phabricator session, it's not necessary to call
        this directly
        """
        req = self.req_session.post('%s/api/conduit.connect' % self.host, data={
            'params': json.dumps(self.connect_params),
            'output': 'json',
            '__conduit__': True,
        })

        # Parse out the response (error handling ommitted)
        result = json.loads(req.content)['result']
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
            req.content,
            object_pairs_hook=collections.OrderedDict
        )['result']
