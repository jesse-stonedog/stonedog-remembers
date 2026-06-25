"""Tests for the synchronous Store facade."""

import json

from roz_remembers import Store, get_nested_value, set_nested_value


def test_set_and_get():
    store = Store({"job": {"bins": 10, "sorted": 0}})
    assert store.get("job.bins") == 10
    assert store.set("job.sorted", 5) is True
    assert store.get("job.sorted") == 5


def test_get_default_for_missing():
    store = Store()
    assert store.get("nope") is None
    assert store.get("a.b.c", default="fallback") == "fallback"


def test_set_creates_intermediate_dicts():
    store = Store()
    assert store.set("machine.state", "IDLE") is True
    assert store.get_state() == {"machine": {"state": "IDLE"}}


def test_set_returns_false_on_bad_traversal():
    store = Store({"items": [1, 2]})
    # index out of range on a list -> failure, state unchanged
    assert store.set("items.5", "x") is False
    assert store.get_state() == {"items": [1, 2]}


def test_get_state_is_a_copy():
    store = Store({"a": {"b": 1}})
    snapshot = store.get_state()
    snapshot["a"]["b"] = 999
    assert store.get("a.b") == 1  # internal state untouched


def test_subscribe_receives_events():
    store = Store({"count": 0})
    events = []
    store.subscribe(events.append)
    store.set("count", 1)
    store.set("count", 2)
    assert [e["new_value"] for e in events] == [1, 2]
    assert events[0]["old_value"] == 0
    assert events[0]["path"] == "count"
    assert events[0]["type"] == "STATE_CHANGED"


def test_unsubscribe_stops_events():
    store = Store()
    events = []
    unsubscribe = store.subscribe(events.append)
    store.set("x", 1)
    unsubscribe()
    store.set("x", 2)
    assert len(events) == 1


def test_failing_subscriber_does_not_break_store():
    store = Store()
    good_events = []

    def boom(_event):
        raise RuntimeError("subscriber failure")

    store.subscribe(boom)
    store.subscribe(good_events.append)
    assert store.set("x", 1) is True  # still succeeds
    assert len(good_events) == 1


def test_load_and_save_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    store = Store({"job": {"bins": 3}})
    store.save(str(path))

    loaded = Store(state_file=str(path))
    assert loaded.get("job.bins") == 3

    # the file is valid JSON
    assert json.loads(path.read_text())["job"]["bins"] == 3


def test_save_without_target_raises():
    store = Store()
    try:
        store.save()
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError when no path/state_file")


def test_module_level_helpers():
    data = {}
    assert set_nested_value("a.b", 1, data) is True
    assert get_nested_value("a.b", data) == 1
    assert get_nested_value("a.missing", data) is None
