import os

import mongomock

from tools.providers import storage_mongo


def test_save_result_with_mongomock(monkeypatch):
    # Reset globals to avoid leaking state between tests
    storage_mongo._client = None
    storage_mongo._collection = None

    fake_client = mongomock.MongoClient()
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGO_DB", "cti_test")
    monkeypatch.setenv("MONGO_COLLECTION", "results_test")
    monkeypatch.setattr(storage_mongo, "MongoClient", lambda uri: fake_client)

    storage_mongo.save_result({"url": "http://ex", "status": "ok"})

    coll = fake_client["cti_test"]["results_test"]
    docs = list(coll.find({}))
    assert len(docs) == 1
    assert docs[0]["url"] == "http://ex"
    assert docs[0]["status"] == "ok"
