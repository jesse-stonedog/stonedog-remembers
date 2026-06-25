# roz-remembers: A Message-Driven State Management Library

---

roz-remembers is a lightweight, message-driven state management library for Python, inspired by the predictable state container pattern popularized by Redux in the JavaScript ecosystem. It's designed to provide a **centralized, immutable state** that can be updated solely through **explicit, descriptive actions**, making your application's state changes predictable, traceable, and easier to debug.

## Features

* **Centralized State:** A single source of truth for your application's state, making it easy to understand and manage.
* **Immutable State:** State is never directly modified. Instead, actions produce new state instances, ensuring data integrity and simplifying change detection.
* **Message-Driven:** All state changes are triggered by dispatching "actions"—plain Python dictionaries describing what happened.
* **Predictable Changes:** Because state changes are a result of explicit actions, it's easy to predict the outcome of any operation.
* **Asynchronous Processing:** Built with `asyncio` to handle actions in a non-blocking, concurrent manner.
* **Initial State Loading:** Supports loading initial state from a JSON file, ideal for configuration or bootstrapping.
* **Action Listeners:** Allows registration of functions that react to specific action types, enabling side effects or complex logic outside the core state update.

## Installation

Roz-Remembers can be installed using [Poetry](https://python-poetry.org/):

```bash
poetry add roz-remembers
```

Or [PIP](https://pypi.org/project/pip/):

```bash
pip install roz-remembers
```

## Two front ends

The library exposes the same dot-path state engine through two APIs.

### `Store` — synchronous (recommended for sync apps)

A simple, observable bag of state for code that does **not** run an asyncio
event loop (for example, the card-sorter device loop):

```python
from roz_remembers import Store

store = Store({"job": {"bins": 10, "sorted": 0}})

store.set("job.sorted", 1)          # dot-path set, returns True/False
store.get("job.sorted")             # -> 1
store.get("job.missing", default=0) # -> 0

# observe changes
unsubscribe = store.subscribe(lambda e: print(e["path"], "->", e["new_value"]))
store.set("machine.state", "CARD_READY")   # auto-creates intermediate dicts

# optional JSON persistence
store.save("state.json")
restored = Store(state_file="state.json")
```

### `RozRemembers` — asynchronous (Redux-style)

The original `asyncio`, action/event-queue store for long-running async
applications:

```python
import asyncio
from roz_remembers import RozRemembers

async def main():
    store = RozRemembers("initial_state.json")
    await store.load_initial_state()
    store.start_processing()

    await store.dispatch({"type": "SET_STATE", "path": "user.theme", "value": "dark"})
    await asyncio.sleep(0.05)
    print(store.get_current_state())

    await store.stop_processing()

asyncio.run(main())
```

Both stores share the dot-path helpers `get_nested_value(path, data)` and
`set_nested_value(path, value, data)`, which are also exported for direct use.

## Development

```bash
pip install pytest pytest-asyncio
PYTHONPATH=src pytest
```

## License

MIT

