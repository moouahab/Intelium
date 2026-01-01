from tools.cache import CacheManager
from tools.providers.http.download_types import DownloadResult
from cti_core.Source import Source
from cti_core.result_recorder import ResultRecorder


class DummyResultStore:
    def __init__(self):
        self.saved = []

    def save(self, result):
        self.saved.append(result)


def test_result_recorder_includes_run_meta(tmp_path):
    cache = CacheManager(tmp_path / "cache.json", auto_save=False)
    results = []
    store = DummyResultStore()
    recorder = ResultRecorder(cache, results, result_store=store, run_meta={"run_id": "run-123"})
    source = Source({"url": "http://example.com", "type": "html", "name": "root"})
    dummy_result = DownloadResult(status="downloaded", content="ok", content_type="text/html")

    recorder.record_result(source, dummy_result, extracted=["ok"], keyword_hits={"indicator": ["ok"]})

    assert results[0]["run_id"] == "run-123"
    assert store.saved[0]["run_id"] == "run-123"
