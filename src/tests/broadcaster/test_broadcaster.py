import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from sockets.process_broadcaster.process_broadcaster import ProcessBroadcaster


@pytest.fixture
def broadcaster_mock():
    patcher = patch("sockets.process_broadcaster.process_broadcaster.BroadCaster")
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def event_loop_mock():
    return MagicMock()


@pytest.fixture
def broadcaster_publish_mock():
    patcher = patch(
        "sockets.process_broadcaster.process_broadcaster.BroadcasterPublish"
    )
    yield patcher.start()
    patcher.stop()


def test_init_sets_properties():
    pb = ProcessBroadcaster(
        broadcast_messages=False,
        redis_host="h",
        redis_port=123,
        redis_database=9,
    )
    assert pb.broadcast_messages is False
    assert pb.redis_host == "h"
    assert pb.redis_port == 123
    assert pb.redis_database == 9


def test_broadcast_messages_property():
    pb = ProcessBroadcaster()
    pb.broadcast_messages = False
    assert pb.broadcast_messages is False
    pb.broadcast_messages = True
    assert pb.broadcast_messages is True


def test_broadcast_channel_property():
    pb = ProcessBroadcaster()
    pb.broadcast_channel = "chan"
    assert pb.broadcast_channel == "chan"


def test_broadcast_channel_raises_if_not_set():
    pb = ProcessBroadcaster()
    with pytest.raises(Exception, match="Must set broadcast channel before broadcast"):
        _ = pb.broadcast_channel


def test_loop_property():
    pb = ProcessBroadcaster()
    loop = MagicMock()
    pb.loop = loop
    assert pb.loop is loop


def test_broadcaster_property_returns_instance(broadcaster_mock):
    pb = ProcessBroadcaster()
    instance = pb.broadcaster
    assert broadcaster_mock.called
    # Should reuse the same instance
    assert pb.broadcaster is instance


@pytest.mark.asyncio
async def test_disconnect_calls_disconnect_on_connected_broadcaster():
    pb = ProcessBroadcaster()
    mock_broadcaster = MagicMock()
    mock_broadcaster.connected = True
    mock_broadcaster.disconnect = AsyncMock()
    pb._broadcaster = mock_broadcaster
    await pb.disconnect()
    mock_broadcaster.disconnect.assert_awaited_once()
    assert mock_broadcaster.connected is False


@pytest.mark.asyncio
async def test_disconnect_does_nothing_if_not_connected():
    pb = ProcessBroadcaster()
    mock_broadcaster = MagicMock()
    mock_broadcaster.connected = False
    mock_broadcaster.disconnect = AsyncMock()
    pb._broadcaster = mock_broadcaster
    await pb.disconnect()
    mock_broadcaster.disconnect.assert_not_awaited()


def test_sync_disconnect_calls_validate_and_disconnect():
    pb = ProcessBroadcaster()
    pb._loop = MagicMock()
    pb.disconnect = AsyncMock()
    pb._loop.run_until_complete = MagicMock()
    pb.sync_disconnect()
    pb._loop.run_until_complete.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_calls_connect_and_publish():
    pb = ProcessBroadcaster()
    pb.broadcast_messages = True
    pb.broadcast_channel = "chan"
    mock_broadcaster = MagicMock()
    mock_broadcaster.connected = False
    mock_broadcaster.connect = AsyncMock()
    mock_broadcaster.publish = AsyncMock()
    pb._broadcaster = mock_broadcaster
    msg = MagicMock()
    await pb.broadcast(msg)
    mock_broadcaster.connect.assert_awaited_once()
    mock_broadcaster.publish.assert_awaited_once_with(channel="chan", message=msg)


@pytest.mark.asyncio
async def test_broadcast_does_nothing_if_broadcast_messages_false():
    pb = ProcessBroadcaster()
    pb.broadcast_messages = False
    pb.broadcast_channel = "chan"
    mock_broadcaster = MagicMock()
    mock_broadcaster.connected = False
    mock_broadcaster.connect = AsyncMock()
    mock_broadcaster.publish = AsyncMock()
    pb._broadcaster = mock_broadcaster
    msg = MagicMock()
    await pb.broadcast(msg)
    mock_broadcaster.connect.assert_not_awaited()
    mock_broadcaster.publish.assert_not_awaited()


def test_sync_broadcast_calls_validate_and_broadcast():
    pb = ProcessBroadcaster()
    pb._loop = MagicMock()
    pb.broadcast = AsyncMock()
    pb._loop.run_until_complete = MagicMock(return_value="result")
    msg = MagicMock()
    result = pb.sync_broadcast(msg)
    pb._loop.run_until_complete.assert_called_once()
    assert result == "result"
