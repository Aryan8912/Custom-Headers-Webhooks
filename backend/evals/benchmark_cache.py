import asyncio
import time
import app.cache as cache_module
import fakeredis.aioredis as fakeredis

async def benchmark_cache():
    cache_module.redis_client = fakeredis.FakeRedis(decode_responses=True)

    iterations = 10000
    test_data = {"tenant_id": "tenant_a", "api_key": "test", "is_active": True}

    # warm cache
    await cache_module.cache_set("tenant:tenant_a", test_data, ttl=300)

    # benchmark cache GET
    start = time.perf_counter()
    hits = 0
    for _ in range(iterations):
        result = await cache_module.cache_get("tenant:tenant_a")
        if result:
            hits += 1
    end = time.perf_counter()

    print(f"Cache GETs : {iterations}")
    print(f"Cache hits : {hits} ({hits/iterations*100:.1f}%)")
    print(f"Total time : {(end-start)*1000:.2f}ms")
    print(f"Per GET    : {(end-start)*1000/iterations:.4f}ms")
    print(f"GETs/sec   : {iterations/(end-start):.0f}")

asyncio.run(benchmark_cache())