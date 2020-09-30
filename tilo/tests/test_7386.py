import time

import structlog

from tilo.clients import PdClient, PlaygroundClient, new_sql_conn
from tilo.clients import wait_till_true

log = structlog.get_logger()


def test_issue_7386():
    log.msg('test 7386')

    pd = PdClient()
    pg = PlaygroundClient()
    conn = new_sql_conn()

    # try to disable auto region-merge
    pd.config_set('disable-remove-extra-replica', 'true')
    pd.config_set('patrol-region-interval', '50000ms')

    with conn.cursor() as cur:
        cur.execute("drop table if exists t;")
        cur.execute("create table t (a int primary key);")
        cur.execute("split table t between (0) and (10000) regions 2;")
        cur.execute("show table t regions;")
        rows = cur.fetchall()
        assert len(rows) == 2
        region_id = rows[1]['REGION_ID']
        target_region_id = rows[0]['REGION_ID']
        log.msg(f'region id: {region_id}, target region id: {target_region_id}')

    # the original peers count is 3
    region = pd.get_region(region_id)
    default_peers_count = len(region['peers'])
    log.msg(f'default peer count {default_peers_count}')

    # get a free store to add learner
    stores = pd.list_stores()
    store_ids = [store['store']['id'] for store in stores
                 if 'labels' not in store['store']]
    log.msg(store_ids)
    used_stores = [peer['store_id'] for peer in region['peers']]
    target_store = [store_id for store_id in store_ids
                    if store_id not in used_stores][0]

    # add learner
    log.msg('add learner and peer for regions')
    ok = pd.add_learner(region_id, target_store)
    assert ok, 'add learner failed'
    # ok = pd.add_peer(target_region_id, target_store)
    # assert ok, 'add peer failed'

    # wait till learner is added
    log.msg('wait till region peers count == 2')
    wait_till_true()(lambda: len(pd.get_region(region_id)['peers']) == default_peers_count + 1)
    # wait_till_true()(lambda: len(pd.get_region(target_region_id)['peers']) == default_peers_count + 1)

    log.msg('sleep for 2s to wait learner apply snapshot')
    time.sleep(2)

    # partition target store
    target_store_port = None
    target_store_pid = None
    for store in stores:
        store_meta = store['store']
        if store_meta['id'] == target_store:
            # port will be the proxy port, for example: 30160
            port = store_meta['address'].split(':')[1]
            # HACK: we convert 30160 to 20160
            target_store_port = '2' + port[1:]
    instances = pg.list_instances()
    for inst in instances:
        if inst.port == target_store_port:
            target_store_pid = inst.pid
    pg.partition(target_store_pid)

    pd.merge_region(region_id, target_region_id)

    input(f'the region id is {region_id}: ')

    pg.unpartition(target_store_pid)
    conn.close()
