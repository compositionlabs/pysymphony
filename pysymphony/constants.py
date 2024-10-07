from enum import Enum

class Status(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    WAITING_FOR_CLIENT_TOOL = "waiting_for_client_tool"

class ToolType(Enum):
    SYMPHONY = "symphony"
    CLIENT = "client"
    API = "api"