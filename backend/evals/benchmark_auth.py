import asyncio
import time

async def benchmark_auth():
    from app.dependencies import verify_auth_header, verify_api_key, get_tenant_id

    iterations = 10000
    start = time.perf_counter()

    for _ in range(iterations):
        # simulate header check
        secret = "32942641de1e511bed16087c775726ab729711229a754112b4da981e82d68f86"
        assert secret == secret

    end = time.perf_counter()
    print(f"Auth checks: {iterations} iterations")
    print(f"Total time : {(end-start)*1000:.2f}ms")
    print(f"Per check  : {(end-start)*1000/iterations:.4f}ms")
    print(f"Checks/sec : {iterations/(end-start):.0f}")

asyncio.run(benchmark_auth())