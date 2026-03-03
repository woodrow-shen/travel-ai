import asyncio
import logging

from app.scheduler import create_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def healthcheck():
    """Simple healthcheck for Docker."""
    return True


async def main():
    logger.info("Starting Travel-AI Price Monitor...")
    scheduler = create_scheduler()
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
