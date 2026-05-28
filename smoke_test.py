import httpx, asyncio

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:8000/api/health")
        assert r.status_code == 200
        print("Smoke test passed")

if __name__ == "__main__":
    asyncio.run(main())
