import httpx


class BaseAPIClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def get(self, path: str, **kwargs) -> dict:
        resp = await self._client.get(path, **kwargs)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, **kwargs) -> dict:
        resp = await self._client.post(path, **kwargs)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
