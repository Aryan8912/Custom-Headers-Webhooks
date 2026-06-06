import asyncio
import time
import uuid
from app.db import AsyncSessionLocal, init_db
from app.models import execution_log, tenant
from app.models.execution_log import ExecutionLog

async def benchmark_db():
    await init_db()

    iterations = 100
    start = time.perf_counter()

    async with AsyncSessionLocal() as db:
        for i in range(iterations):
            log = ExecutionLog(
                id=str(uuid.uuid4()),
                execution_id=f"bench_{i}",
                agent_id="agent_001",
                tenant_id="tenant_a",
                status="completed",
                payload={"execution_id": f"bench_{i}", "status": "completed"},
                auth_verified=True,
                forwarded=False,
            )
            db.add(log)
        await db.commit()

    end = time.perf_counter()
    print(f"DB writes  : {iterations} rows")
    print(f"Total time : {(end-start)*1000:.2f}ms")
    print(f"Per write  : {(end-start)*1000/iterations:.2f}ms")
    print(f"Writes/sec : {iterations/(end-start):.0f}")

asyncio.run(benchmark_db())