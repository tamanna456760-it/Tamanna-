from event_logger import log_event
from heartbeat_manager import HeartbeatManager

heartbeat = HeartbeatManager()

heartbeat.update("node-1")

log_event("Server Started")

print("Server Core Running")
