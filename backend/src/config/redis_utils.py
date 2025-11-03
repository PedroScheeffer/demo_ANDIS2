import json
from config.redis_client import redis_client

QUEUE_NAME = "project_creation_queue"

def enqueue_project_task(project_data, user_id):
    task = {
        "user_id": user_id,
        "project_data": project_data.dict() if hasattr(project_data, "dict") else project_data
    }
    redis_client.rpush(QUEUE_NAME, json.dumps(task))