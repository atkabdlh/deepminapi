import psutil
import os
import logging

logger = logging.getLogger(__name__)

_peak_memory = {}

def log_memory_usage(context="", pid=None):
    """
    Logs current and peak memory usage for a given process.
    If pid is None, uses current process.
    """
    if pid is None:
        pid = os.getpid()
    process = psutil.Process(pid)
    mem_info = process.memory_info()
    
    rss_mb = mem_info.rss / 1024 / 1024
    vms_mb = mem_info.vms / 1024 / 1024
    
    # Track peak memory per PID
    prev_peak = _peak_memory.get(pid, 0)
    if rss_mb > prev_peak:
        _peak_memory[pid] = rss_mb
    
    logger.info(
        f"[MEM] PID={pid} {context} | "
        f"RSS={rss_mb:.2f} MB, VMS={vms_mb:.2f} MB, "
        f"Peak={_peak_memory[pid]:.2f} MB"
    )