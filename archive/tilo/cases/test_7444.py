from tilo.clients import PdClient, PlaygroundClient, new_sql_conn


def test_pull_7444():
    pd = PdClient()
    conn = new_sql_conn()
    pg = PlaygroundClient()

    # try to disable auto region-merge
    pd.config_set('disable-remove-extra-replica', 'true')
    pd.config_set('patrol-region-interval', '50000ms')

    with conn.cursor() as cur:
        cur.execute("drop table if exists t;")
        cur.execute("create table t (a int primary key);")
        cur.execute("split table t between (0) and (10000) regions 3;")
        cur.execute("show table t regions;")
        rows = cur.fetchall()

        regions = []
        for row in rows:
            regions.append((row['REGION_ID'], row['START_KEY']))
        regions = sorted(regions, key=lambda v: v[1])

        # insert data into three regions
        cur.execute("insert into t values (1111), (4444), (7777);")
        cur.execute("select * from t;")
        print(cur.fetchall())

    print('three regions have been created')

    assert len(regions) == 3
    left, center, right = regions[0][0], regions[1][0], regions[2][0]

    instances = pg.list_instances()
    stores = pd.list_stores()
    tikvs = {}  # {port: store_id}
    for store in stores:
        store_meta = store['store']
        # port will be the proxy port, for example: 30160
        port = store_meta['address'].split(':')[1]
        # HACK: we convert 30160 to 20160
        port = '2' + port[1:]
        tikvs[port] =  store_meta['id']

    # [(store_id, pid, port), ]
    pg_stores = []
    for instance in instances:
        port = str(instance.port)
        store_id = tikvs.get(port)
        if store_id is not None:
            pg_stores.append((store_id, instance.pid, port))

    print(pg_stores)
    print('transfer leader', left, pg_stores[0][0])
    print('transfer leader', right, pg_stores[0][0])
    print('transfer leader', center, pg_stores[1][0])
    # transfer left&right to pg_stores 0
    pd.transfer_leader(left, pg_stores[0][0])
    pd.transfer_leader(right, pg_stores[0][0])
    # transfer center to pg_stores 1
    pd.transfer_leader(center, pg_stores[1][0])

    # wait for the leader to transfere
    time.sleep(1)
    log.msg('wait for leader transfer')
    wait_till_true()(lambda: pd.get_region(left)['leader']['store_id'] == pg_stores[0][0])
    wait_till_true()(lambda: pd.get_region(right)['leader']['store_id'] == pg_stores[0][0])
    wait_till_true()(lambda: pd.get_region(center)['leader']['store_id'] == pg_stores[1][0])
    print('leader transfer finished')
    # partition pg_stores 2
    log.msg(f'partition store {pg_stores[2][0]}')
    assert pg.partition(pg_stores[2][1]) is True

    # merge left&right to center, and wait
    print('merge region begin')
    while True:
        if pd.merge_region(left, center):
            break
        time.sleep(1)
    while True:
        if pd.merge_region(right, center):
            break
        time.sleep(1)
    print('merge region finished')

    with conn.cursor() as cur:
        while True:
            time.sleep(1)
            cur.execute("show table t regions")
            rows = cur.fetchall()

            # left and right region are merged into center region
            if len(rows) == 1:
                assert rows[0]['REGION_ID'] == center
                break

    # insert data to center region
    with conn.cursor() as cur:
        cur.execute("insert into t values (2222), (5555), (8888);")

    # manual check log
    print('please check log', pg_stores[2], center)
    input()

    # recover pg_stores 2 network
    log.msg(f'unpartition store {pg_stores[2][0]}')
    assert pg.unpartition(pg_stores[2][1]) is True
    assert pg.unpartition(pg_stores[1][1]) is True

    pd.transfer_leader(center, pg_stores[2][0])
    wait_till_true()(lambda: pd.get_region(center)['leader']['store_id'] == pg_stores[2][0])

    with conn.cursor() as cur:
        cur.execute("insert into t values (3333), (6666), (9999);")
        cur.execute("select * from t;")
        print(cur.fetchall())
