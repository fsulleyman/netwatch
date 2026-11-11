import psutil
import time
from datetime import datetime

CPU_CORES = psutil.cpu_count() or 1

# Prime the counters so the first real reading isn't 0
psutil.cpu_percent(interval=None)
for _p in psutil.process_iter(["cpu_percent"]):
    pass


def get_top_processes(limit=5):
    """Return the busiest processes by CPU, then memory."""
    processes = []

    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"] or "unknown",
                # psutil reports per-core totals, so divide to get a 0-100 scale
                "cpu": round((info["cpu_percent"] or 0) / CPU_CORES, 1),
                "memory": round(info["memory_percent"] or 0, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda p: (p["cpu"], p["memory"]), reverse=True)
    return processes[:limit]


def get_system_metrics():
    # CPU usage (non-blocking: measured since the previous call)
    cpu_usage = psutil.cpu_percent(interval=None)

    # Memory usage
    memory = psutil.virtual_memory()

    # Disk usage
    disk = psutil.disk_usage("/")

    # Network statistics
    network = psutil.net_io_counters()

    # System uptime
    uptime_seconds = time.time() - psutil.boot_time()

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "cpu": {
            "usage": cpu_usage,
            "cores": CPU_CORES
        },

        "memory": {
            "total": round(memory.total / (1024 ** 3), 2),
            "used": round(memory.used / (1024 ** 3), 2),
            "percentage": memory.percent
        },

        "disk": {
            "total": round(disk.total / (1024 ** 3), 2),
            "used": round(disk.used / (1024 ** 3), 2),
            "percentage": disk.percent
        },

        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv
        },

        "processes": get_top_processes(),

        "uptime": round(uptime_seconds / 3600, 2)
    }