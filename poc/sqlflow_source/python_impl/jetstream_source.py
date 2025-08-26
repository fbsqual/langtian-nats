# minimal jetstream source PoC
import asyncio
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect()
    js = nc.jetstream()
    sub = await js.subscribe('battery.telemetry')
    async for msg in sub.messages:
        print('got', msg)

if __name__ == '__main__':
    asyncio.run(main())