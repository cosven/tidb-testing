import time
from collections import namedtuple
from urllib.parse import urlparse

import requests
import pymysql
import structlog


log = structlog.get_logger()


def new_sql_conn(db_uri='mysql://root@127.0.0.1:4000'):
    """
    1. random choose one connection info
    2. create a connection and use test database
    """
    result = urlparse(db_uri)
    return pymysql.connect(host=result.hostname,
                           port=result.port,
                           user=result.username,
                           password=result.password or '',

                           db='test',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)


def wait_till_true(interval=1):
    def wrapper(func, *args, **kwargs):
        while True:
         if func(*args, **kwargs) is True:
             break
         time.sleep(interval)
    return wrapper


class PdClient:
    def __init__(self, url='http://127.0.0.1:2379'):
        self._url = url
        self._pd_api = f'{url}/pd/api/v1'

    def add_learner(self, region_id, store_id):
        js = {
            'name': 'add-learner',
            'region_id': region_id,
            'store_id': store_id,
        }
        return self._add_operator(js)

    def add_peer(self, region_id, store_id):
        js = {
            'name': 'add-peer',
            'region_id': region_id,
            'store_id': store_id,
        }
        return self._add_operator(js)

    def remove_peer(self, region_id, store_id):
        js = {
            'name': 'remove-peer',
            'region_id': region_id,
            'store_id': store_id,
        }
        return self._add_operator(js)

    def merge_region(self, source_region_id, target_region_id):
        js = {
            'name': 'merge-region',
            'source_region_id': source_region_id,
            'target_region_id': target_region_id,
        }
        return self._add_operator(js)

    def transfer_leader(self, region_id, store_id):
        js = {
            'name': 'transfer-leader',
            'region_id': region_id,
            'to_store_id': store_id,
        }
        return self._add_operator(js)

    def _add_operator(self, js):
        log.msg('add opereator', **js)
        resp = requests.post(f'{self._pd_api}/operators', json=js)
        if resp.status_code == 200:
            return True
        log.debug(f'failed: {resp.text}', **js)
        return False

    def config_set(self, key, value):
        js = {
            key: value
        }
        resp = requests.post(f'{self._pd_api}/config', json=js)
        return resp.status_code == 200

    def get_region(self, region_id):
        resp = requests.get(f'{self._pd_api}/region/id/{region_id}')
        js = resp.json()
        return js

    def list_stores(self):
        resp = requests.get(f'{self._pd_api}/stores')
        js = resp.json()
        return js['stores']

    def apply_placement_rule(self, js):
        log.msg(f'apply placement rule', rule=js)
        resp = requests.post(f'{self._pd_api}/config/rule', json=js)
        if resp.status_code == 200:
            return True
        log.debug(f'failed: {resp.text}')
        return False


PlaygroundInstance = namedtuple('PlaygroundInstance', ['pid', 'role', 'uptime', 'port'])


class PlaygroundClient:
    def __init__(self, url='http://127.0.0.1:9527'):
        self._url = url

    def list_instances(self):
        resp = self._send_command('display')
        instances = []
        for line in resp.text.split('\n')[2:]:
            parts = line.split()
            if len(parts) == 4:
                instance = PlaygroundInstance(*parts)
                instances.append(instance)
        return instances

    def partition(self, pid):
        resp = self._send_command('partition', pid)
        return resp.status_code == 200

    def unpartition(self, pid):
        resp = self._send_command('unpartition', pid)
        return resp.status_code == 200

    def _send_command(self, cmd_type, pid=None):
        js = {
            'CommandType': cmd_type,
        }
        if pid is not None:
            js['PID'] = int(pid)
        return requests.post(f'{self._url}/command', json=js)
