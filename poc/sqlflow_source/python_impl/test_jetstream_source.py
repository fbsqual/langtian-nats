import asyncio
import pytest
from jetstream_source import JetStreamSource

@pytest.mark.asyncio
async def test_connect_fetch_or_skip():
    src = JetStreamSource()
    try:
        await src.connect()
    except Exception as e:
        pytest.skip(f'nats not available: {e}')
    recs = await src.fetch_once()
    assert isinstance(recs, list)
    await src.close()
