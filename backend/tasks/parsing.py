import asyncio

from celery_app import celery_app
from parsers.streaming_parsers import StreamingParser

streaming_parsers = StreamingParser()


@celery_app.task(bind=True, name="tasks.parse_file")
def parse_file_task(self, file_id: int, file_path: str, repository_id: str):
    """Parse file with batch support for large files"""
    if streaming_parsers.should_stream(file_path):
        asyncio.run(_par)
