import json
from backend.app.services.memory_capture_service import MemoryCaptureService

memory_service = MemoryCaptureService()

with open("backend/data/sample_memories.json") as f:
    memories = json.load(f)

for m in memories:
    memory_service.create_memory(m)

print("Memories loaded:", len(memories))
