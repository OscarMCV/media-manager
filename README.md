# Media Manager

A Python project for managing media and broadcasting messages between processes using Redis and websockets.

## Features

- Process broadcasting with Redis backend
- Asynchronous and synchronous broadcasting support
- Progress calculation utility

## Requirements

- Python 3.10+
- Redis server (for broadcasting)
- See `pyproject.toml` for dependencies

## Installation

Clone the repository and install dependencies:

```sh
git clone <your-repo-url>
cd media-manager
pip install .
```

Or for development:

```sh
pip install -e .[dev]
```

## Usage

### Broadcasting Example

```python
from sockets.process_broadcaster.process_broadcaster import ProcessBroadcaster
from sockets.broadcaster.schemas import BroadcasterPublish

pb = ProcessBroadcaster()
pb.broadcast_channel = "my_channel"

import asyncio
pb.loop = asyncio.get_event_loop()

# Asynchronous broadcast
async def main():
    msg = BroadcasterPublish(data="Hello World")
    await pb.broadcast(msg)

asyncio.run(main())

# Synchronous broadcast
msg = BroadcasterPublish(data="Hello World")
pb.sync_broadcast(msg)
```

### Progress Calculation

```python
progress = pb.calculate_progress(current_element=5, total_elements=10)
print(progress)  # 50
```

## Running Tests

Tests are located in `src/tests/`. Run them with:

```sh
pytest
```

## Project Structure

```
src/
  sockets/
    broadcaster/
    process_broadcaster/
  tests/
```

## License

MIT License

---

**Author:** OscarMCV
**Contact:** oscarm.cabrerav@gmail.com
