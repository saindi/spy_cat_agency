import aiohttp

from loguru import logger

from app.core import settings


class CatBreedService:
    _instance = None
    _breeds: set | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def load_breeds(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.cat_api.BREED_URL) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self._prepare_breed(data=data)
                    logger.info(f"Loaded {len(self._breeds)} breeds")
        except Exception as e:
            logger.error(f"[CatBreedService] Failed to load breeds: {e}")
            self._breeds = set()

    def _prepare_breed(self, data: list[dict]) -> None:
        self._breeds = {b["name"] for b in data}

    async def is_valid_breed(self, breed: str) -> bool:
        if self._breeds is None:
            await self.load_breeds()

        return breed in self._breeds


cat_api_service = CatBreedService()
