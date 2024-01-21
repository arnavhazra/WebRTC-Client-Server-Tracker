import pytest
import asyncio
from multiprocessing import Value
from unittest.mock import Mock, patch
from client import process_a, handle_track, run
from server import BallBouncingVideoStreamTrack, run as server_run

def test_process_a():
    queue = Mock()
    queue.get.return_value = Mock()
    coordinates = Value('d', 0.0)
    process_a(queue, coordinates)
    queue.get.assert_called_once()

@pytest.mark.asyncio
async def test_handle_track():
    track = Mock()
    track.recv.return_value = Mock()
    queue = Mock()
    channel = Mock()
    coordinates = Value('d', 0.0)
    await handle_track(track, queue, channel, coordinates)
    track.recv.assert_called_once()
    queue.put.assert_called_once()
    channel.send.assert_called_once()

@pytest.mark.asyncio
async def test_client_run():
    pc = Mock()
    signaling = Mock()
    queue = Mock()
    coordinates = Value('d', 0.0)
    with patch('client.handle_track') as mock_handle_track:
        await run(pc, signaling, queue, coordinates)
    pc.createDataChannel.assert_called_once()
    signaling.connect.assert_called_once()
    signaling.receive.assert_called_once()
    pc.setRemoteDescription.assert_called_once()
    pc.setLocalDescription.assert_called_once()
    signaling.send.assert_called_once()

def test_BallBouncingVideoStreamTrack():
    track = BallBouncingVideoStreamTrack()
    assert track.ball_pos == [0, 0]
    assert track.ball_vel == [3, 3]

@pytest.mark.asyncio
async def test_server_run():
    pc = Mock()
    signaling = Mock()
    local_video = BallBouncingVideoStreamTrack()
    await server_run(pc, signaling, local_video)
    pc.createDataChannel.assert_called_once()
    signaling.connect.assert_called_once()
    pc.setLocalDescription.assert_called_once()
    signaling.send.assert_called_once()
    signaling.receive.assert_called_once()
    pc.setRemoteDescription.assert_called_once()