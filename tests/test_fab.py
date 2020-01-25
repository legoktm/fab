from pathlib import Path
import json
import pytest

import phabricator

root = Path(__file__).parent.parent
config = json.load((root / "test_config.json").open(encoding="utf-8"))


def test_invalid_config():
    try:
        phabricator.Phabricator(config['host'], config['username'])
        pytest.fail()
    except ValueError:
        pass


def test_token():
    phab = phabricator.Phabricator(config['host'], config['username'], token=config['token'])

    result = phab.request('user.whoami')

    assert result['userName'] == config['username']


def test_certificate():
    """Deprecated certificate-based authentication"""
    phab = phabricator.Phabricator(config['host'], config['username'], cert=config['certificate'])

    result = phab.request('user.whoami')

    assert result['userName'] == config['username']


def test_error():
    phab = phabricator.Phabricator(config['host'], config['username'], token=config['token'])

    try:
        phab.request('user.transactions')
        pytest.fail()
    except phabricator.PhabricatorException as e:
        assert e.error_code == "ERR-CONDUIT-CORE"
        assert e.error_info == "Only admins can call this API"
