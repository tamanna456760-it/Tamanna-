from datetime import datetime

import psutil


def collect_server_metrics():
    return {
        "timestamp": str(datetime.utcnow()),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }


if __name__ == "__main__":
    print(collect_server_metrics())
