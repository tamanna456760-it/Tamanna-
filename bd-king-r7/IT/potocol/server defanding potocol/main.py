from heartbeat_manager import HeartbeatManager
from event_logger import log_event

heartbeat = HeartbeatManager()

heartbeat.update("node-1")

log_event("Server Started")

print("Server Core Running")