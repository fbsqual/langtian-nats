import asyncio
import json
import logging
from nats.aio.client import Client as NATS

log = logging.getLogger(__name__)

class JetStreamSource:
    def __init__(self, url='nats://127.0.0.1:4222', subject='battery.telemetry', durable='sqlflow_durable', batch=10, timeout=1.0):
        self.url = url
        self.subject = subject
        self.durable = durable
        self.batch = batch
        self.timeout = timeout
        self.nc = NATS()

    async def connect(self):
        try:
            await asyncio.wait_for(self.nc.connect(self.url), timeout=5.0)
            # jetstream() may be synchronous in some nats-py versions; handle both
            try:
                self.js = await self.nc.jetstream()
            except TypeError:
                # older/newer APIs might return directly
                self.js = self.nc.jetstream()
        except Exception as e:
            log.warning(f'Failed to connect to NATS at {self.url}: {e}')
            raise

    async def fetch_once(self):
        # Best-effort: if JetStream APIs aren't available or fail, return empty list instead of crashing
        try:
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
            records = []
            for m in msgs:
                try:
                    records.append(m.data)
                    await m.ack()
                except Exception:
                    # swallow per-message ack errors in PoC
                    pass
            return records
        except Exception as e:
            log.warning(f'JetStream fetch failed: {e}; returning empty list')
            # Fallback: attempt a short-lived plain subscription poll if possible
            try:
                sub = await self.nc.subscribe(self.subject)
                recs = []
                try:
                    for _ in range(self.batch):
                        msg = await asyncio.wait_for(sub.next_msg(), timeout=self.timeout)
                        recs.append(msg.data)
                except Exception:
                    pass
                try:
                    await sub.unsubscribe()
                except Exception:
                    pass
                return recs
            except Exception:
                return []

    async def close(self):
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
