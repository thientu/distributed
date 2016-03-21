import json

from distributed.utils_test import gen_cluster, div
from distributed.diagnostics.scheduler import status, workers
from distributed.executor import _wait

@gen_cluster(executor=True)
def test_status(e, s, a, b):
    d = status(s)

    assert d['failed'] == 0
    assert d['in-memory'] == 0
    assert d['ready'] == 0
    assert d['tasks'] == 0
    assert d['waiting'] == 0

    L = e.map(div, range(10), range(10))
    yield _wait(L)

    d = status(s)
    assert d['failed'] == 1
    assert d['in-memory'] == 9
    assert d['ready'] == 0
    assert d['tasks'] == 10
    assert d['waiting'] == 0
    assert all(v > 0 for v in d['bytes'].values())


@gen_cluster(executor=True)
def test_workers(e, s, a, b):
    while 'latency' not in s.host_info[a.ip]:
        yield gen.sleep(0.01)
    d = workers(s)

    assert json.loads(json.dumps(d)) == d

    assert 0 <= d[a.ip]['cpu'] <= 100
    assert 0 <= d[a.ip]['latency'] <= 2
    assert 0 <= d[a.ip]['available-memory'] < d[a.ip]['total-memory']
    assert set(map(int, d[a.ip]['ports'])) == {a.port, b.port}
    assert d[a.ip]['processing'] == {}
    assert d[a.ip]['last-seen'] > 0

    L = e.map(div, range(10), range(10))
    yield _wait(L)

    assert 0 <= d[a.ip]['cpu'] <= 100
    assert 0 <= d[a.ip]['latency'] <= 2
    assert 0 <= d[a.ip]['available-memory'] < d[a.ip]['total-memory']
    assert set(map(int, d[a.ip]['ports'])) == {a.port, b.port}
    assert d[a.ip]['processing'] == {}
