import uuid


async def gen_unique_filename():
    return str(uuid.uuid4())
