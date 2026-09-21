#!/usr/bin/env python3

import asyncio, httpx, time
async def main():
    url="http://localhost:8080/movies/1/stats"
    start=time.time()
    async with httpx.AsyncClient(timeout=20) as c:
        async def fetch(idx):
            print(f"  [{idx}] sent -> GET {url}", flush=True)
            t0=time.time()
            r = await c.get(url)
            dt=time.time()-t0
            print(f"  [{idx}] received <- {r.status_code} in {dt:.2f}s", flush=True)
            return r
        rs=await asyncio.gather(*[fetch(i) for i in range(10)])
        codes=[r.status_code for r in rs]
        print(f"  200={codes.count(200)} 429={codes.count(429)}")
        for r in rs:
            if r.status_code==429:
                print(f"    429 body: {r.text[:120]}")
        print(f"  elapsed {time.time()-start:.2f}s")

        async def fetch_health(idx):
            hurl="http://localhost:8080/health"
            print(f"  [health {idx}] sent -> GET {hurl}", flush=True)
            t0=time.time()
            r = await c.get(hurl)
            dt=time.time()-t0
            print(f"  [health {idx}] received <- {r.status_code} in {dt:.2f}s", flush=True)
            return r
        _ = await asyncio.gather(*[fetch_health(i) for i in range(5)])
asyncio.run(main())
