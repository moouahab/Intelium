from tools.providers import storage_mongo


class DummyColl:
    def insert_one(self, doc):
        doc["_id"] = "dummy"  # simulate pymongo adding _id
        return doc


def test_save_result_does_not_mutate_original(monkeypatch):
    inserted = {}

    def fake_get_collection():
        return DummyColl()

    monkeypatch.setattr(storage_mongo, "_get_collection", fake_get_collection)

    payload = {"url": "http://example.com", "status": "ok"}
    storage_mongo.save_result(payload)

    # original payload should not be altered by _id injection
    assert "_id" not in payload
