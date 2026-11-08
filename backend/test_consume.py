import asyncio
from database import SessionLocal
from main import consume_addon
from fastapi import Request
import schemas

class DummyRequest:
    async def json(self):
        return {"addon_name": "Treadmill 12-session"}

async def test():
    async with SessionLocal() as db:
        try:
            member = await consume_addon(2, DummyRequest(), db)
            print(member.id)
            print("OK!")
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test())
