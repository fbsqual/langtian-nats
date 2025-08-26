import asyncio
import json
import logging
from typing import Any, List
from nats.aio.client import Client as NATS

log = logging.getLogger(__name__)


def _decode_payload(data: bytes) -> Any:
    """Attempt to decode payload as JSON, otherwise return raw bytes/utf-8 string."""
    if data is None:
        return None
    try:
        text = data.decode('utf-8')
    except Exception:
        return data
    try:
        return json.loads(text)
    except Exception:
        return text


class JetStreamSource:
    def __init__(self, url: str = 'nats://127.0.0.1:4222', subject: str = 'battery.telemetry', durable: str = 'sqlflow_durable', batch: int = 10, timeout: float = 1.0):
        self.url = url
        self.subject = subject
        self.durable = durable
        self.batch = batch
        self.timeout = timeout
        self.nc = NATS()
        self.js = None

    async def connect(self) -> None:
        try:
            await asyncio.wait_for(self.nc.connect(self.url), timeout=5.0)
            # jetstream() may be synchronous in some nats-py versions; handle both
            try:
                self.js = await self.nc.jetstream()
            except TypeError:
                self.js = self.nc.jetstream()
            log.info('Connected to NATS %s, subject=%s', self.url, self.subject)
        except Exception as e:
            log.warning('Failed to connect to NATS at %s: %s', self.url, e)
            raise

    async def fetch_once(self) -> List[Any]:
        """Fetch a single batch of messages, decode payloads where possible.

        Returns a list of decoded payloads (json/object/str/bytes).
        """
        # Best-effort: if JetStream APIs aren't available or fail, return empty list instead of crashing
        try:
            if self.js is None:
                log.debug('JetStream context not available; attempting to refresh')
                try:
                    self.js = await self.nc.jetstream()
                except Exception:
                    pass

            # Ensure a stream exists (idempotent for PoC)
            try:
                await self.js.add_stream(name='POC_STREAM', subjects=[self.subject])
            except Exception:
                pass

            # Create or ensure consumer
            try:
                await self.js.add_consumer(stream='POC_STREAM', durable_name=self.durable, deliver_policy='all')
            except Exception:
                pass

            # Attempt pull fetch
            msgs = await self.js.fetch(self.durable, batch=self.batch, timeout=self.timeout)
            records: List[Any] = []
            for m in msgs:
                try:
                    records.append(_decode_payload(m.data))
                    await m.ack()
                except Exception:
                    # swallow per-message ack errors in PoC
                    log.debug('message ack failed', exc_info=True)
            return records
        except Exception as e:
            log.warning('JetStream fetch failed: %s; falling back to plain subscribe', e)
            # Fallback: attempt a short-lived plain subscription poll if possible
            try:
                sub = await self.nc.subscribe(self.subject)
                recs: List[Any] = []
                try:
                    for _ in range(self.batch):
                        msg = await asyncio.wait_for(sub.next_msg(), timeout=self.timeout)
                        recs.append(_decode_payload(msg.data))
                except Exception:
                    pass
                try:
                    await sub.unsubscribe()
                except Exception:
                    pass
                return recs
            except Exception:
                return []

    async def close(self) -> None:
        try:
            await self.nc.drain()
        except Exception:
            pass
        try:
            await self.nc.close()
        except Exception:
            pass


if __name__ == '__main__':
    async def main():
        src = JetStreamSource()
        await src.connect()
        recs = await src.fetch_once()
        print(f'Fetched {len(recs)}')
        await src.close()

    asyncio.run(main())
