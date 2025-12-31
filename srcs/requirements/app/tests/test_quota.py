from tools.quota import Quota


def test_quota_pages_and_bytes():
    q = Quota(max_pages=2, max_bytes=100)
    assert q.reserve_page() is True
    assert q.reserve_page() is True
    assert q.reserve_page() is False  # dépassement

    assert q.add_bytes(50) is True
    assert q.add_bytes(40) is True
    assert q.add_bytes(20) is False  # dépassement
