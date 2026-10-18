import asyncio

async def task_a():
    await asyncio.sleep(5)
    print("A finished")

async def task_b():
    await asyncio.sleep(2)
    print("B finished")

async def main():
    await asyncio.gather(task_a(), task_b())

asyncio.run(main())