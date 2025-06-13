from pymongo.errors import CollectionInvalid
from app.mongo.mongo_client import Mongo


async def init_mongo_collections():
    async with Mongo() as db:
        if "reviews" not in await db.list_collection_names():
            try:
                await db.create_collection("reviews")
            except CollectionInvalid:
                pass

        await db["reviews"].create_index("user_id")
        await db["reviews"].create_index("product_id")
        await db["reviews"].create_index("created_at")
