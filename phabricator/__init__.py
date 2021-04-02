#!/usr/bin/env python
"""
Copyright (C) 2014, 2018, 2020-2021 Kunal Mehta <legoktm@debian.org>
Copyright (C) 2020 Merlijn van Deen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import collections
import hashlib
import json
import requests
import time

__version__ = '3.0.0'


class PhabricatorException(Exception):
    def __init__(self, response: dict):
        error_code = response.get('error_code', 'UNKNOWN')
        error_info = response.get('error_info', 'UNKNOWN')

        super().__init__('{}: {}'.format(error_code, error_info))
        self.error_code = error_code
        self.error_info = error_info
        self.response = response


class Phabricator:
    def __init__(self, host: str, user: str, cert: str = None, token: str = None,
                 user_agent: str = None):
        """
        :param host: Hostname of the Phabricator instance, with no trailing /
        :param user: Your username
        :param cert: The conduit certificate, available in your settings
        :param token: conduit API token, available in your settings
        :param user_agent: User-agent to set
        """
        self.host = host
        self.user = user
        self.cert = cert
        self.phab_session = {}
        self.token = token
        self.user_agent = user_agent
        self.req_session = requests.Session()

    @property
    def headers(self) -> dict:
        ret = {}
        if self.user_agent is not None:
            ret['user-agent'] = self.user_agent
        return ret

    @property
    def connect_params(self) -> dict:
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
        }, headers=self.headers)

        # Parse out the response (error handling ommitted)
        result = req.json()['result']
        self.phab_session = {
            'sessionKey': result['sessionKey'],
            'connectionID': result['connectionID'],
        }

    def request(self, method: str, params: dict = None) -> dict:
        """
        Make a request to a method in the phabricator API
        :param method: Name of the API method to call
        :param params: Optional dict of params to pass
        :raises PhabricatorException
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
        }, headers=self.headers)
        response = json.loads(
            req.content.decode(),
            object_pairs_hook=collections.OrderedDict
        )

        if response.get('error_code') is not None:
            raise PhabricatorException(response)

        return response['result']
