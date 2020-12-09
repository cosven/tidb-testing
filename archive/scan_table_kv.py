import asyncio

from tikv_client.asynchronous import RawClient
from tilo.codec.bytes_ import encode_bytes
from tilo.codec.number import encode_int


async def scan_mvcc_delete_records(table_id):
    client = await RawClient.connect('127.0.0.1:2379')

    key_t = encode_int(b't', int(table_id))
    start_key = encode_int(key_t + b'_i', 0)
    start_key = encode_bytes(b'', start_key)
    # _s > _r > _i
    end_key = encode_bytes(b'', key_t + b'_s')

    delete_count = 0

    def analysis(kvs):
        nonlocal delete_count
        total = 0
        for k, v in kvs.items():
            print(len(v))
            if v[:1] == b'D':
                total += 1
        delete_count += total
        print(f'analysis {len(kvs)} kvs, {total} deletes')


    while True:
        limit = 5000
        kvs = await client.scan(start_key,
                                end=end_key,
                                limit=limit,
                                cf='write')
        analysis(kvs)
        if len(kvs) < limit:
            break
        else:
            start_key = max(kvs)

    print('delete count:', delete_count)


if __name__ == '__main__':
    import sys

    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_mvcc_delete_records(int(sys.argv[1])))
