import json
import time
from redis import Redis
from repos.project_repository import ProjectRepository
from services.project_service import ProjectService

redis_client = Redis(host="redis", port=6379, decode_responses=True)
project_repo = ProjectRepository()
project_service = ProjectService()

QUEUE_NAME = "project_creation_queue"

print("Worker listening for project creation tasks...")

while True:
    task = redis_client.blpop(QUEUE_NAME, timeout=0)  # espera bloqueante
    _, data = task
    payload = json.loads(data)
    
    user_id = payload["user_id"]
    project_data = payload["project_data"]

    print(f"Creating project for user {user_id}...")

    try:
        project_repo.create(project_data, user_id)
        project_service.delete_cache()
        print("Project created successfully.")
    except Exception as e:
        print(f"Error creating project: {e}")
    
    time.sleep(0.1)
