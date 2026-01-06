from prometheus_client import Gauge, REGISTRY
import psutil


def register_metric(name, description):
    try:
        return Gauge(name, description, registry=REGISTRY)
    except ValueError:
        return REGISTRY._names_to_collectors[name]


CPU_USAGE = register_metric("process_cpu_percent", "CPU usage percent")
MEMORY_USAGE = register_metric("process_memory_bytes", "Memory usage in bytes")
THREAD_COUNT = register_metric("process_thread_count", "Thread count")


def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=None))
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    THREAD_COUNT.set(psutil.cpu_count() or 0)
