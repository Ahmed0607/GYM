import asyncio
import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from database import get_db
import models
from database import engine

async def fix_addons_usage():
    async for db in get_db():
        result = await db.execute(select(models.Subscription))
        subscriptions = result.scalars().all()
        for sub in subscriptions:
            if isinstance(sub.addons_usage, list):
                new_addons_usage = {}
                for item in sub.addons_usage:
                    if isinstance(item, dict) and "name" in item:
                        # Converting from list to dict
                        new_addons_usage[item["name"]] = {
                            "total": item.get("total"),
                            "used": item.get("attended", item.get("used", 0))
                        }
                sub.addons_usage = new_addons_usage
                flag_modified(sub, "addons_usage")
        await db.commit()
        print("Updated existing subscriptions.")
        break

if __name__ == "__main__":
    asyncio.run(fix_addons_usage())
